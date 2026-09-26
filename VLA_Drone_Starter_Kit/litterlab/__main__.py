import argparse
import csv
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from .core import (Field, CATEGORIES, DT, HEIGHT, classical, policy_features,
                   parse_instruction, detect_and_map)
from .learning import TinyPolicy, train


def fresh(path):
    path=Path(path); path.mkdir(parents=True, exist_ok=False); return path


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2))


def rollout(seed, target, mode="classical", model=None, language="normal", response=1.):
    if language not in {"normal", "swapped", "empty"}:
        raise ValueError("Unknown language condition")
    if model is None and language != "normal":
        raise ValueError("Language interventions require a learned model")
    env=Field(seed, response=response); steps=[]; frames=[]; dwell=0
    instruction_target=target if language=="normal" else ((target+1)%3 if language=="swapped" else None)
    input_task="" if instruction_target is None else f"centre above the {CATEGORIES[instruction_target]}"
    for k in range(60):
        obs=env.observe()
        if model is not None:
            action=model.action(policy_features(obs,instruction_target))
        elif mode=="expert":
            action=env.expert(target)
        else:
            action=classical(obs,target)
        record={"step":k,"capture_time_s":obs.capture_time,
                "instruction":input_task,
                "position_ned_m":[*obs.position.tolist(),-HEIGHT],
                "velocity_ned_m_s":[*obs.velocity.tolist(),0.],
                "state":[*obs.velocity.tolist(),HEIGHT,0.,0.,0.,1.],
                "action_delta_ne_m":action.tolist()}
        absolute=env.apply(action)
        record["accepted_position_ne_m"]=absolute.tolist()
        record["frame"]=f"{k:04d}.png"
        steps.append(record); frames.append(obs.image)
        dwell=dwell+1 if env.success(target) else 0
        if dwell>=2:
            break
    return env, steps, frames, dwell>=2


def save_visuals(out, frames, steps, env):
    images=out/"frames"; images.mkdir()
    animated=[]
    for im,row in zip(frames,steps):
        im.save(images/row["frame"])
        canvas=im.resize((384,384),Image.Resampling.NEAREST)
        d=ImageDraw.Draw(canvas); d.line((182,192,202,192),fill="white");d.line((192,182,192,202),fill="white")
        d.text((8,8),f't={row["capture_time_s"]:.1f}s',fill="white")
        animated.append(canvas)
    animated[0].save(out/"replay.gif",save_all=True,append_images=animated[1:],duration=250,loop=0)
    # A plot made without matplotlib, with north up and east right.
    chart=Image.new("RGB",(600,600),"white");d=ImageDraw.Draw(chart)
    def px(point): return (300+float(point[1])*55,300-float(point[0])*55)
    d.rectangle((25,25,575,575),outline=(0,51,153),width=2)
    d.text((270,8),"NORTH",fill="black");d.text((525,580),"EAST",fill="black")
    for cat,q in env.objects:
        u,v=px(q); d.ellipse((u-5,v-5,u+5,v+5),fill=(255,102,0));d.text((u+8,v),CATEGORIES[cat],fill="black")
    trace=[px(row["position_ned_m"][:2]) for row in steps]+[px(env.position)]
    d.line(trace,fill=(0,51,153),width=3)
    chart.save(out/"trajectory.png")


def demo(args):
    out=fresh(args.out);target=parse_instruction(args.target)
    model=TinyPolicy.load(args.model) if args.model else None
    env,steps,frames,success=rollout(args.seed,target,model=model)
    save_visuals(out,frames,steps,env)
    (out/"steps.jsonl").write_text("\n".join(json.dumps(s) for s in steps)+"\n")
    # Toy world has one instance per category; this key is not a real tracker.
    tracks={}
    for im,row in zip(frames,steps):
        from .core import Observation
        obs=Observation(im,np.array(row["position_ned_m"][:2]),np.array(row["velocity_ned_m_s"][:2]),row["capture_time_s"])
        for item in detect_and_map(obs): tracks[item["category"]]=item
    dump(out/"map_local.json",{"coordinate_system":"local NED metres, NOT GeoJSON", "objects":list(tracks.values())})
    result={"success":success,"steps":len(steps),"elapsed_sim_s":env.time,"seed":args.seed,
            "target":CATEGORIES[target],"policy":"tiny learned baseline" if model else "classical colour baseline"}
    dump(out/"result.json",result);print(json.dumps(result,indent=2))


def collect(args):
    out=fresh(args.out); x=[];y=[];splits=[]; episode_index=[]; manifest=[]
    for split,count,base in [("train",args.train,0),("val",args.val,100000),("test",args.test,200000)]:
        for i in range(count):
            seed=base+i; target=i%3
            env,steps,frames,success=rollout(seed,target,mode="expert")
            ep=f"{split}_{i:04d}"; folder=out/ep;folder.mkdir();(folder/"images").mkdir()
            for im,row in zip(frames,steps):
                from .core import Observation
                obs=Observation(im,np.array(row["position_ned_m"][:2]),np.array(row["velocity_ned_m_s"][:2]),row["capture_time_s"])
                x.append(policy_features(obs,target));y.append(row["action_delta_ne_m"])
                splits.append(split);episode_index.append(ep)
                im.save(folder/"images"/row["frame"])
            (folder/"steps.jsonl").write_text("\n".join(json.dumps(s) for s in steps)+"\n")
            dump(folder/"evaluator_only.json",{"objects":[{"category":CATEGORIES[c],"ne_m":q.tolist()} for c,q in env.objects]})
            manifest.append({"episode_id":ep,"split":split,"seed":seed,"target":CATEGORIES[target],"success":success,"steps":len(steps)})
    np.savez_compressed(out/"samples.npz",x=np.array(x,dtype=np.float32),y=np.array(y,dtype=np.float32),
                        split=np.array(splits),episode_id=np.array(episode_index))
    dump(out/"manifest.json",{"format":"litterlab-1","fps":2,"action_schema":"delta_NE_metres_capture_anchor",
                            "camera":"level_nadir_96px_f48_height5m", "episodes":manifest})
    print(json.dumps({"episodes":len(manifest),"samples":len(x),"expert_failures":sum(not e["success"] for e in manifest)},indent=2))


def evaluate(args):
    if args.model is None and args.language != "normal":
        raise ValueError("Language interventions require a learned model")
    base={"val":100000,"test":200000}[args.split]
    out=fresh(args.out); model=TinyPolicy.load(args.model) if args.model else None
    rows=[]
    # Same frozen seeds and requested targets in all conditions.
    for i in range(args.episodes):
        target=i%3
        env,steps,frames,success=rollout(base+i,target,model=model,language=args.language,response=args.response)
        point=next(q for c,q in env.objects if c==target)
        rows.append({"seed":base+i,"target":CATEGORIES[target],"input_task":steps[0]["instruction"],"success":success,
                     "error_m":float(np.linalg.norm(env.position-point)),"elapsed_sim_s":env.time})
    dump(out/"trials.json",rows)
    report={"episodes":len(rows),"success_count":sum(r["success"] for r in rows),
            "success_rate":sum(r["success"] for r in rows)/len(rows),
            "mean_final_error_m":float(np.mean([r["error_m"] for r in rows])),
            "split":args.split,"language_condition":args.language,"response_multiplier":args.response,
            "domain":"toy kinematic simulation only"}
    dump(out/"summary.json",report);print(json.dumps(report,indent=2))


def main():
    ap=argparse.ArgumentParser(description="Offline litter-navigation teaching exercises")
    sub=ap.add_subparsers(dest="command",required=True)
    d=sub.add_parser("demo");d.add_argument("--out",required=True);d.add_argument("--target",default="can")
    d.add_argument("--seed",type=int,default=7);d.add_argument("--model");d.set_defaults(func=demo)
    c=sub.add_parser("collect");c.add_argument("--out",required=True)
    c.add_argument("--train",type=int,default=150);c.add_argument("--val",type=int,default=30);c.add_argument("--test",type=int,default=30);c.set_defaults(func=collect)
    t=sub.add_parser("train");t.add_argument("--data",required=True);t.add_argument("--out",required=True)
    t.add_argument("--epochs",type=int,default=200);t.add_argument("--seed",type=int,default=0)
    t.set_defaults(func=lambda a:print(json.dumps(train(a.data,a.out,a.epochs,a.seed),indent=2)))
    e=sub.add_parser("evaluate");e.add_argument("--out",required=True);e.add_argument("--model")
    e.add_argument("--split",choices=["val","test"],default="val",help="validation by default; reserve test for final comparisons")
    e.add_argument("--episodes",type=int,default=30);e.add_argument("--language",choices=["normal","swapped","empty"],default="normal")
    e.add_argument("--response",type=float,default=1.);e.set_defaults(func=evaluate)
    args=ap.parse_args()
    if hasattr(args,"episodes") and args.episodes<1:ap.error("episodes must be positive")
    if hasattr(args,"response") and args.response<=0:ap.error("response must be positive")
    if args.command=="evaluate" and args.model is None and args.language!="normal":
        ap.error("--language swapped/empty requires --model")
    args.func(args)


if __name__=="__main__":main()

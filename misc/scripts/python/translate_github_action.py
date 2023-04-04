import argparse
import os
import yaml


def Header(action_path):
    return f"# DO NOT MODIFY: Auto-generated by the gen_installer.py script from the {action_path} Github Action"


def ConvertStep(step):
    # update submodules
    if step.get("uses", "").startswith("actions/checkout"):
        if step.get("with", {}).get("submodules", False) == True:
            return "git submodule update --init"
    # comment out sudo actions
    command = step.get("run", "")
    return command.replace("sudo", "#sudo")


def ShellExtension(system):
    if "windows" in system:
        return "ps1"
    else:
        return "sh"


def OutputEnvironment(env, system):
    if "windows" in system:
        exports = [f"$env:{name} = '{value}'" for name, value in env.items()]
    else:
        exports = [f"export {name}='{value}'" for name, value in env.items()]
    return "\n".join(exports)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate xpano installer script from a Github Action"
    )
    parser.add_argument("action_path", help="Path to the Github Action YAML file")
    parser.add_argument(
        "--output_dir", help="Path to the Github Action YAML file", default=""
    )
    args = parser.parse_args()

    with open(args.action_path, "r") as file:
        action = yaml.safe_load(file)

    env = action.get("env", {})

    for job_name, job in action["jobs"].items():
        system = job["runs-on"]
        filename = "{}.{}".format(job_name, ShellExtension(system))

        header = Header(args.action_path)
        exports = OutputEnvironment(env, system)
        script = "\n".join(ConvertStep(step) for step in job["steps"])

        with open(os.path.join(args.output_dir, filename), "w") as file:
            file.write(header)
            file.write("\n\n")
            file.write(exports)
            file.write("\n\n")
            file.write(script)

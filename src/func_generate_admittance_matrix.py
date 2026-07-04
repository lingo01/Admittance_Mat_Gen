import argparse
import json
import time

import cloudpss
import numpy as np
from pandapower import runpp

from func_cdf2mpc import func_cdf2mpc
from func_cdf_normalization import func_cdf_normalization
from func_cloudpss_config import func_inject_cloudpss_config
from func_process_messages_for_cdf import func_process_messages_for_cdf


POWER_FLOW_JOB_NAME = "Power Flow Job: Admittance Mat Generation"


def __get_from_ppc_converter():
    try:
        from pandapower.converter.pypower.from_ppc import from_ppc
        return from_ppc
    except ImportError:
        pass

    try:
        import pandapower.converter
        return pandapower.converter.from_ppc
    except AttributeError as exc:
        raise RuntimeError(
            "Cannot find pandapower from_ppc converter. Please check your pandapower version."
        ) from exc


def func_generate_admittance_matrix(project_name, area_name):
    server_name, token, user_name = func_inject_cloudpss_config()
    model = cloudpss.Model.fetch(f'model/{user_name}/{project_name}')
    job = model.getModelJob(POWER_FLOW_JOB_NAME)

    if len(job) < 1:
        job = model.createJob("powerFlow", POWER_FLOW_JOB_NAME)
        job['args']['Method'] = 'common_format'
        model.addJob(job)
        model.save()
        job = model.getModelJob(POWER_FLOW_JOB_NAME)

    model.runner = model.runPowerFlow(job[0])
    print("--Power flow calculation running", end="")
    while model.runner.status() == 0:
        print(".", end="")
        time.sleep(1)
    print(".")

    if model.runner.status() == -1:
        raise RuntimeError("Power flow calculation failed")

    print("--Power flow calculation completed")

    messages = model.runner.result.db.message
    cdf_files = func_process_messages_for_cdf(messages, "cf.zip", area_name)
    cdf_content = func_cdf_normalization(cdf_content=cdf_files["cf"])
    cdf_map = json.loads(cdf_files["cf_map"])

    mpc, warnings = func_cdf2mpc(
        cdf_file_name=f"{area_name}.cf",
        cdf_content=cdf_content,
    )

    mpc['areas'] = np.array([[1]])
    from_ppc = __get_from_ppc_converter()
    net = from_ppc(mpc)
    runpp(net)
    Ybus = net["_ppc"]["internal"]["Ybus"]

    return Ybus, cdf_map


def __print_bus_mapping(cdf_map, model):
    bus_idx = 1
    for bus in cdf_map.get('buses', []):
        bus_key = bus['bus']['component']
        if isinstance(bus_key, str) and bus_key.startswith('/'):
            bus_key = bus_key[1:]

        comp = model.getComponentByKey(bus_key)
        bus_name = getattr(comp, 'label', None) or getattr(comp, 'name', f"<component {bus_key}>")
        print(f"BUS {bus_idx}-th in Ybus corresponds to {bus_name} in the actual system")
        bus_idx += 1


def __parse_args():
    parser = argparse.ArgumentParser(description="Generate Ybus and CDF map from a CloudPSS project.")
    parser.add_argument("--project-name", required=True, help="CloudPSS project name.")
    parser.add_argument("--area-name", required=True, help="CDF area name, for example area1.")
    return parser.parse_args()


def func_generate_admittance_matrix_cli():
    args = __parse_args()
    Ybus, cdf_map = func_generate_admittance_matrix(args.project_name, args.area_name)

    print("*******************************************")
    print("System admittance matrix Ybus:")
    print("*******************************************")
    print(Ybus)

    print("*******************************************")
    print("Ybus bus order mapping:")
    print("*******************************************")
    server_name, token, user_name = func_inject_cloudpss_config()
    model = cloudpss.Model.fetch(f'model/{user_name}/{args.project_name}')
    __print_bus_mapping(cdf_map, model)

    return Ybus, cdf_map


if __name__ == "__main__":
    func_generate_admittance_matrix_cli()

# server.py
import inspect
import os
import tempfile
from typing import Annotated, Literal
from pydantic import Field
from mcp.server import FastMCP

from aap_inventory_tool import generate_command

PORT = int(os.getenv("PORT", "20000"))
HOST = os.getenv("HOST", "127.0.0.1")

mcp = FastMCP(
    "AI Installer Template MCP Server",
    host=HOST,
    port=PORT,
)


@mcp.tool(
    name="get_inventory",
    description="Get AAP(Ansible Automation Patform) 2.5 inventory file in INI format.",
)
def get_inventory(
        platform: Annotated[
            Literal['containerized', 'rpm'],
            Field(description='Platform type (containerized or rpm)'),
        ],
        topology: Annotated[
            Literal['growth', 'enterprise'],
            Field(description='Topology type (growth or enterprise)'),
        ],
        # required for containerized growth topology
        host: Annotated[
            str,
            Field(description='Host (hostname or IP) for all-in-one deployment (required for containerized growth topology)'),
        ] = '',
        # required both for containerized and RPM enterprise topologies
        gateway_hosts: Annotated[
            str,
            Field(description='Gateway hosts [comma-delimited host names or IP addresses] (required for containerized enterprise topology and RPM enterprise topology, minimum 2 hosts)'),
        ] = '',
        controller_hosts: Annotated[
            str,
            Field(description='Controller hosts [comma-delimited host names or IP addresses] (required for containerized enterprise topology and RPM enterprise topology, minimum 2 hosts)'),
        ] = '',
        hop_host: Annotated[
            str,
            Field(description='Hop host (required for containerized enterprise topology and RPM enterprise topology)'),
        ] = '',
        execution_hosts: Annotated[
            str,
            Field(description='Execution node hosts [comma-delimited host names or IP addresses] (required for containerized enterprise topology and RPM enterprise topology, minimum 2 hosts)'),
        ] = '',
        hub_hosts:  Annotated[
            str,
            Field(description='Automation Hub hosts [comma-delimited host names or IP addresses] (required for containerized enterprise topology and RPM enterprise topology, minimum 2 hosts)'),
        ] = '',
        eda_hosts: Annotated[
            str,
            Field(description='EDA Controller hosts [comma-delimited host names or IP addresses] (required for containerized enterprise topology and RPM enterprise topology, minimum 2 hosts)'),
        ] = '',
        external_database: Annotated[
            str,
            Field(description='External database host (required for containerized enterprise topology and RPM enterprise topology)'),
        ] = '',
        # RPM specfic arguments
        gateway_host: Annotated[
            str,
            Field(description='Gateway host (required for RPM growth topology)'),
        ] = '',
        controller_host: Annotated[
            str,
            Field(description='Controller host (required for RPM growth topology)'),
        ] = '',
        execution_host: Annotated[
            str,
            Field(description='Execution host (required for RPM growth topology)'),
        ] = '',
        hub_host: Annotated[
            str,
            Field(description='Hub host (required for RPM growth topology)'),
        ] = '',
        eda_host: Annotated[
            str,
            Field(description='EDA host (required for RPM growth topology)'),
        ] = '',
        database_host: Annotated[
            str,
            Field(description='Database host (required for RPM growth topology)'),
        ] = '',
        redis:  Annotated[
            str,
            Field(description='Redis cluster hosts [comma-delimited host names or IP addresses] (optional for enterprise topologies, requires exactly 6 hosts. If not provided, uses 2 gateway + 2 hub + 2 eda hosts)'),
        ] = '',
        # Custom CA certificate parameters
        custom_ca_cert: Annotated[
            str,
            Field(description='Path to custom CA certificate file (optional). If specified without value, will create templated variable.'),
        ] = '',
        ca_tls_cert: Annotated[
            str,
            Field(description='Path to CA TLS certificate file (optional). If specified without value, will create templated variable.'),
        ] = '',
        ca_tls_key: Annotated[
            str,
            Field(description='Path to CA TLS certificate file (optional). If specified without value, will create templated variable.''Path to CA TLS key file (optional). If specified without value, will create templated variable.'),
        ] = '',
        # Hub signing parameters
        hub_signing_auto_sign: Annotated[
            str,
            Field(description='Enable automatic signing for hub collections. If specified without value, will create templated variable.'),
        ] = '',
        hub_signing_require_content_approval: Annotated[
            str,
            Field(description='Require content approval for hub collections. If specified without value, will create templated variable.'),
        ] = '',
        hub_signing_collection_key: Annotated[
            str,
            Field(description='Path to collection signing key. If specified without value, will create templated variable.'),
        ] = '',
        hub_signing_collection_pass: Annotated[
            str,
            Field(description='Passphrase for collection signing key. If specified without value, will create templated variable.'),
        ] = '',
        hub_signing_container_key: Annotated[
            str,
            Field(description='Path to container signing key. If specified without value, will create templated variable.'),
        ] = '',
        hub_signing_container_pass: Annotated[
            str,
            Field(description='Passphrase for container signing key. If specified without value, will create templated variable.'),
        ] = '',
        session_id: Annotated[
            str,
            Field(description='This is a dummy argument added only for llama-stack compatibility'),
        ] = '',
) -> str:
    # Read arguments and convert them into the format used by Python's argparse.ArgumentParser
    frame = inspect.currentframe()
    args_dict = inspect.getargvalues(frame).locals

    class Args:
        pass

    args = Args()
    for k,v in args_dict.items():
        # Ignore session_id, which is added only for Llama Stack compatibility.
        if k != "session_id":
            # Convert string properties that contain a comma-delimited list into a list.
            if k == "redis" or k.endswith("_hosts") and v is not None:
                v = [s.strip() for s in v.split(",") if s != ""]
            setattr(args, k, v)

    # Create temporary files for inventory and log
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as inventory_file:
            args.output_path = inventory_file.name
            with tempfile.NamedTemporaryFile(delete=False, mode="w") as log:
                # Generate an AAP inventory
                rc = generate_command(args, log)

                # If the inventory file was generated successfully, return it.
                if rc == 0:
                    with open(inventory_file.name) as f:
                        output = f.read()
                # Otherise, return the execution log.
                else:
                    with open(log.name) as f:
                        output = f.read()
                        print(output)
                return output
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f'An unexpected error occurred.'




if __name__ == "__main__":
    mcp.run(transport="sse")

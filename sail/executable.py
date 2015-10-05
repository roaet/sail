#
# Copyright 2015 Justin Hammond
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import click
import configobj

import sail.services.network as net
import sail.session as session
import sail.task
import sail.utils.auth as auth
import sail.exceptions.common as exc


command_settings = {
    'ignore_unknown_options': True,
}


def _load_config(file):
    try:
        config = configobj.ConfigObj(file, raise_errors=True)
        return config
    except configobj.ParseError as e:
        raise exc.ParsingError(e)


@click.command(context_settings=command_settings)
@click.option('--auth-config-file', default=None, is_flag=False,
              type=click.File('rb'),
              help="Authentication configuration file")
@click.option('--net-config-file', default=None, is_flag=False,
              type=click.File('rb'),
              help="Network service configuration file")
@click.option('--verbose', default=False, is_flag=True,
              help="Toggle verbosity of output")
@click.pass_context
def run_sail(ctx, auth_config_file, net_config_file, verbose):
    if verbose:
        ctx.verbose = True
    conf = None
    if auth_config_file is not None:
        conf = _load_config(auth_config_file)
    auth_info = auth.do_auth(ctx, conf)
    ctx.auth_info = auth_info

    if ctx.verbose:
        click.echo("Auth token: %s" % auth_info.token)

    conf = None
    if net_config_file is not None:
        conf = _load_config(net_config_file)
    net_srv = net.Network(conf)

    ctx.session = session.Session()

    """
    Some defaults for giggles
    net_info =  {"network": {"name": "derp"}}

    subnet_info = {"subnet": {"name": "derp", "network_id": net_id,
                              "cidr": "192.168.0.0/24", "ip_version": 4}}
    port_info = {"port": {"network_id": net_id}}
    port_info = {"port": {"network_id": net_id}}
    ip_info = {"ip_address": {"network_id": net_id, "version": 4,
                              "port_ids": [port_id1, port_id2]}}
    """
    with ctx.session.setUp(auth_info, [net_srv]):
        net.GetNetworks()()
        create = net.CreateNetwork()()
        net.DeleteNetwork(notify_success=[create])()
    ctx.exit(0)

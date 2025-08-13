import os
import csv
import subprocess
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
import ssl
import socket
from datetime import datetime
import json


def azure_login_and_set_subscription(tenant_id: str, subscription_id: str):
    login_command = f"az login --tenant {tenant_id}"
    subprocess.run(login_command, shell=True, check=True)

    set_subscription_command = f"az account set --subscription {subscription_id}"
    subprocess.run(set_subscription_command, shell=True, check=True)

    print(f"Successfully logged in to tenant {tenant_id} and set subscription {subscription_id}\n")


def get_endpoints(tenant_id: str, subscription_id: str, resource_group_name: str, app_gateway_name: str) -> set:
    azure_login_and_set_subscription(tenant_id, subscription_id)
    credential = DefaultAzureCredential()
    network_client = NetworkManagementClient(credential, subscription_id)

    app_gateway = network_client.application_gateways.get(resource_group_name, app_gateway_name)

    endpoints = set()
    for listener in app_gateway.http_listeners:
        if listener.protocol == 'Https' and listener.host_name and listener.frontend_port.id:
            port = listener.frontend_port.id.split('/')[-1].split('_')[-1]
            endpoints.add(f"{listener.host_name}:{port}")

    print("Found the following domains:")
    for endpoint in sorted(endpoints):
        print(endpoint)
    print()
    return sorted(endpoints)


def get_cert_info(endpoint: set):
    domain, port = endpoint.split(':')
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, port)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as secure_sock:
                cert = secure_sock.getpeercert()

        subject = dict(x[0] for x in cert['subject'])
        issuer = dict(x[0] for x in cert['issuer'])
        return {
            'Domain': domain,
            'Port': port,
            'Subject': subject.get('commonName', 'N/A'),
            'Issuer': issuer.get('commonName', 'N/A'),
            'ValidFrom': datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z').isoformat(),
            'ValidTo': datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z').isoformat(),
            'SerialNumber': cert.get('serialNumber', 'N/A'),
            'Version': cert.get('version', 'N/A'),
            'Status': 'Valid'
        }
    except Exception as e:
        return {
            'Domain': domain,
            'Port': port,
            'Subject': 'N/A',
            'Issuer': 'N/A',
            'ValidFrom': 'N/A',
            'ValidTo': 'N/A',
            'SerialNumber': 'N/A',
            'Version': 'N/A',
            'Status': f'Error: {str(e)}'
        }


def ensure_directory_exists(file_path: str):
    # 파일 경로에서 디렉토리 부분만 추출
    directory = os.path.dirname(file_path)

    # 디렉토리가 비어있지 않고 존재하지 않는 경우에만 생성
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"Directory created: {directory}")
        except OSError as e:
            print(f"Error occurred while creating directory: {e}")
    elif directory:
        print(f"Directory already exists: {directory}")
    else:
        print("File will be saved in the current directory.")


def main():
    with open('settings/JPF-HUB-APPGW.settings.json', 'r') as file :
        config = json.load(file)
    tenant_id = config['tenantId']
    subscription_id = config['subscriptionId']
    resource_group_name = config['appgwRgName']
    app_gateway_name = config['appgwName']
    csv_path = config['resultFileName']
    ensure_directory_exists(csv_path)

    endpoints = get_endpoints(tenant_id, subscription_id, resource_group_name, app_gateway_name)
    # endpoints = {
    #     "dev-jpartners.hyundaijapan.com:8081",
    #     "dev-jpartners.hyundaijapan.com:9091",
    #     "stg-jpartners.hyundaijapan.com:8081",
    #     "stg-jpartners.hyundaijapan.com:9091",
    #     "jpartners.hyundaijapan.com:443",
    #     "jpartners.hyundaijapan.com:9091"
    # }

    # Check TLS certificate for each domain
    results = []
    for endpoint in endpoints:
        print(f"Checking certificate for {endpoint}")
        cert_info = get_cert_info(endpoint)
        results.append(cert_info)

        for key, value in cert_info.items():
            print(f"{key}: {value}")
        print()

    # Save results to CSV
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Domain', 'Port', 'Subject', 'Issuer', 'ValidFrom', 'ValidTo', 'SerialNumber', 'Version', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print(f"Results have been saved to {csv_path}")


if __name__ == "__main__":
    main()
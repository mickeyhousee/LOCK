import subprocess
import os

# Função para instalar serviço usando systemctl
def install_service(file_path, service_file_path, service_name):
    print("Installing Service")
    with open(service_file_path, 'r') as arquivo:
        linhas = arquivo.readlines()

    for i, linha in enumerate(linhas):
        if linha.startswith("ExecStart="):
            linhas[i] = f"ExecStart={file_path}\n"

    with open(service_file_path, 'w') as arquivo:
        arquivo.writelines(linhas)
    try:

        subprocess.run(['chmod', '+x', file_path], check=True)

        # Comando para copiar o arquivo de serviço para o diretório apropriado
        subprocess.run(['cp', service_file_path, f'/etc/systemd/system/'], check=True)
        
        # Comando para recarregar os serviços Systemctl
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        
        # Comando para ativar o serviço
        subprocess.run(['sudo', 'systemctl', 'enable', service_name], check=True)
        
        # Comando para iniciar o serviço
        subprocess.run(['sudo', 'systemctl', 'start', service_name], check=True)
        
        print(f'Serviço {service_name} instalado e iniciado com sucesso!')
    except subprocess.CalledProcessError as e:
        print(f'Ocorreu um erro ao instalar o serviço {service_name}: {e}')
    print("Serviço instalado com sucesso!")



# Função para parar serviço usando systemctl
def stop_service():
    subprocess.run(['sudo', 'systemctl', 'stop', 'ufw'], check=True)
    print("Parando serviço...")
    # Comandos para parar o serviço aqui
    print("Serviço parado com sucesso!")




def start_service(service_name):
    subprocess.run(['sudo', 'systemctl', 'start', service_name], check=True)
    print("Serviço Iniciado com sucesso!")


# Função para exibir o menu do script "Backup"
def backup_menu():
    while True:
        print("\nMenu do script \"Backup\":")
        print("1. Instalar serviço (systemctl)")
        print("2. Start \"Backup\" service")
        print("3. Stop \"Backup\" service")
        print("4. Voltar")

        option = input("Opção: ")

        if option == "1":
            install_service()
        elif option == "2":
            start_service()
        elif option == "3":
            stop_service()
        elif option == "4":
            break
        else:
            print("Opção inválida!")

# Função para exibir o menu do script "ServiceMonitor"
def service_monitor_menu():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = f"{dir_path}/modules/servicemonitor/servicemonitor.py"
    service_file_path = "/modules/servicemonitor/servicemonitor.service"
    service_name = "servicemonitor"
    while True:
        print("\nMenu do script \"ServiceMonitor\":")
        print("1. Instalar serviço (systemctl)")
        print("2. Start \"Backup\" ServiceMonitor")
        print("3. Stop \"Backup\" ServiceMonitor")
        print("4. Voltar")

        option = input("Opção: ")

        if option == "1":
            install_service(file_path,service_file_path, service_name)

        elif option == "2":
            start_service(service_name)
        elif option == "3":
            stop_service()
        elif option == "4":
            break
        else:
            print("Opção inválida!")

# Loop principal do menu
while True:
    print("\nSelecione uma opção:")
    print("1. Script \"Backup\"")
    print("2. Script \"ServiceMonitor\"")
    print("3. Sair")

    option = input("Opção: ")

    if option == "1":
        backup_menu()
    elif option == "2":
        service_monitor_menu()
    elif option == "3":
        print("Saindo...")
        break
    else:
        print("Opção inválida!")
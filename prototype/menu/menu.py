import subprocess

# Função para instalar serviço usando systemctl
def install_service(service_name, service_file_path):
    print("Instalando serviço...")
    try:
        # Comando para copiar o arquivo de serviço para o diretório apropriado
        subprocess.run(['sudo', 'cp', service_file_path, f'/etc/systemd/system/{service_name}.service'], check=True)
        
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
    print("Parando serviço...")
    # Comandos para parar o serviço aqui
    print("Serviço parado com sucesso!")

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
    while True:
        print("\nMenu do script \"ServiceMonitor\":")
        print("1. Instalar serviço (systemctl)")
        print("2. Start \"Backup\" ServiceMonitor")
        print("3. Stop \"Backup\" ServiceMonitor")
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
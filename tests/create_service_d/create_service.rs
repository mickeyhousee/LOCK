use std::fs;
use std::io::Write;
use std::path::Path;
use std::time::Duration;
use std::process::Command;

fn main() {
    // Define o diretório de logs
    let log_dir = "/home/joaog/logs";

    // Define o intervalo de tempo para apagar os arquivos (5 minutos)
    let intervalo = Duration::from_secs(300);

    // Cria o conteúdo do arquivo de serviço
    let conteudo_servico = format!(
        r#"
[Unit]
Description=Loop 1 minuto Ola to notas.txt
After=multi-user.target

[Service]
ExecStart=/home/joaog/Desktop/LOCK/tests/loop_1min_ola_to_a_file/loop_ola
Type=simple

[Install]
WantedBy=multi-user.target
        "#
    );

    // Escreve o conteúdo do arquivo de serviço
    let mut arquivo_servico = fs::OpenOptions::new()
        .write(true)
        .create(true)
        .open("/etc/systemd/system/loop_ola.service")
        .unwrap();
    arquivo_servico.write_all(conteudo_servico.as_bytes()).unwrap();

    // Recarrega os serviços do systemd
    let mut comando = Command::new("systemctl");
    comando.arg("daemon-reload");
    comando.spawn().unwrap().wait().unwrap();

    // Inicia o serviço
    comando.arg("start");
    comando.arg("loop_ola.service");
    comando.spawn().unwrap().wait().unwrap();

    println!("Serviço criado e iniciado com sucesso!");
}
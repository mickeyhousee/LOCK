use std::fs::OpenOptions;
use std::io::Write;
use std::thread::sleep;
use std::time::Duration;

fn main() {
    // Define o arquivo de notas
    let arquivo_notas = "/home/joaog/notas.txt";

    loop {
        // Escreve "Olá" no arquivo de notas
        let mut arquivo = OpenOptions::new()
            .write(true)
            .append(true)
            .open(arquivo_notas)
            .unwrap();
        arquivo.write_all(b"Ola\n").unwrap();

        // Espera 1 minuto
        sleep(Duration::from_secs(60));
    }
}

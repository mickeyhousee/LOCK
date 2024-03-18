use std::fs;

fn main() {
  let filename = "teste.txt";
  let contents = fs::read_to_string(filename)
    .expect("Failed to read file");

  println!("File contents: {}", contents);
}

use as_bytes::AsBytes;
use sha1::{Sha1, Digest};
use std::fs::{File, OpenOptions};
use std::io::{self, Read, Write};

fn main() -> Result<(), std::io::Error> {
    // Specify the file path to hash
    let path = "/home/joaog/LOCK/rust_exercicies/mini_projects/hello_world";

    // Open the file for reading
    let mut file = File::open(path)?;

    // Create a new SHA-1 hasher
    let mut hasher = Sha1::new();

    // Create a buffered reader for efficient reading
    let mut reader = io::BufReader::new(file);

    // Buffer for reading file contents in chunks
    let mut buf = [0; 4096];

    // Loop for reading and hashing the file in chunks
    loop {
        let bytes_read = reader.read(&mut buf)?;

        // Check for end of file
        if bytes_read == 0 {
            break;
        }

        hasher.update(&buf[..bytes_read]);
    }

    // Finalize the SHA-1 hash calculation
    let hash = hasher.finalize();

    // Create "hashs.hash" file with write permissions, creating it if needed
    let mut hash_file = OpenOptions::new()
        .create(true) // Create the file if it doesn't exist
        .write(true)
        .open("hashs.hash")?;

    // Write the SHA-1 hash as bytes to the file (using unsafe block)
    unsafe {
        hash_file.write_all(hash.as_bytes())?;
    }

    println!("SHA-1 hash: {:x?}", hash);
    println!("Hash saved to hashs.hash");

    Ok(())
}

// Import necessary libraries
use sha1::{Sha1, Digest}; // Provide SHA-1 hashing functionality
use std::fs::File;         // For opening files
use std::io::{self, Read};  // For reading file contents and error handling

// Define the main function, handling potential errors
fn main() -> Result<(), std::io::Error> {
    // Specify the file path to hash (replace with your actual path)
    let path = "/home/joaog/LOCK/rust_exercicies/mini_projects/hello_world";

    // Open the file, handling potential errors
    let mut file = File::open(path)?;

    // Create a new SHA-1 hasher to compute the hash
    let mut hasher = Sha1::new();

    // Create a buffered reader for efficient file reading
    let mut reader = io::BufReader::new(file);

    // Buffer for reading file contents in chunks
    let mut buf = [0; 4096];

    // Loop for reading and hashing the file in chunks
    loop {
        // Read a chunk of data into the buffer
        let bytes_read = reader.read(&mut buf)?;

        // If no bytes were read, we've reached the end of the file
        if bytes_read == 0 {
            break;
        }

        // Update the SHA-1 hash with the read bytes
        hasher.update(&buf[..bytes_read]);
    }

    // Finalize the SHA-1 hash calculation
    let hash = hasher.finalize();

    // Print the calculated SHA-1 hash
    println!("SHA-1 hash: {:x?}", hash);

    // Indicate successful execution
    Ok(())
}

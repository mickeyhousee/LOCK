use std::fs; // Import the `fs` module for file system operations
use std::io; // Import the `io` module for input/output operations
use std::path::Path; // Import the `Path` module for working with file paths

fn main() -> io::Result<()> {
    // The main function is the program's entry point. It returns a Result type
    // indicating either success (Ok) or an error (io::Error)

    // Define the secure folder name
    let secure_folder = "best_folder_ever_made";

    // Define the backup folder name
    let backup_folder = "super_secure_folder";

    // Create the backup folder if it doesn't exist
    if !Path::new(backup_folder).exists() {
        fs::create_dir(backup_folder)?; // Attempt to create the backup folder
    }

    // Loop through files in the secure folder
    for entry in fs::read_dir(secure_folder)? {
        let entry = entry?; // Extract the directory entry from the iterator
        let filename = entry.file_name().to_str().unwrap().to_owned(); // Make a copy
        let source_path = Path::new(&secure_folder).join(filename.clone()); // Construct source path
        let destination_path = Path::new(&backup_folder).join(filename); // Construct destination path
        fs::copy(source_path, destination_path)?; // Copy the file
    }

    println!("Backup created successfully!");

    Ok(()) // Return Ok to indicate successful execution
}

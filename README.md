# LOCK
Projeto LOCK criado no âmbito do curso avançado de programação

![alt text](assets/L.png)

## Compile rust

To Compile a rust program we need to install this:

### For Windows:

https://www.rust-lang.org/tools/install

### For Linux:

```bash
sudo apt install rustc
```

### To compile

To compile just run this:

```bash
rustc nameofyourprogram
```

In windows, this command will generate a .exe

In linux, this command will generate a .bat

## How to create a new project in Rust with cargo

```bash
$ cargo new calculator
```
This creates a new directory named calculator, initialises it as a Git repository, and adds useful boilerplate for your project.

The boilerplate includes:

**Cargo.toml** – The manifest file used by Cargo to manage your project's metadata

**src/** – The directory where your project code should live

**src/main.rs** – The default file Cargo uses as your application entrypoint

The calculator/Cargo.toml file contains the following:

```bash
[package]
name = "calculator"
version = "0.1.0"
edition = "2018"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
```

The **[package]** denotes your project's metadata.

The **[dependencies]** heading denotes the crates your project depends on. Crates are like external libraries.

The **calculator/src/main.rs** file contains the following:

```bash
fn main() {
  println!("Hello, world!");
}
```

This file contains a function declaration with the handle **main**. By default, rustc calls the **main** function first whenever the executable is run.

**println!** is a built-in macro which prints to the console.

### Run the Project

You can either use Cargo to run your project code:

```bash
# Within the calculator/ directory
$ cargo run
   Compiling fcc-rust-in-replit v0.1.0 (/home/runner/Rust-in-Replit-1)
    Finished dev [unoptimized + debuginfo] target(s) in 0.80s
     Running `target/debug/calculator`
Hello, world!
```
Or, you can use rustc to compile your project, then you can run the binary:

```bash
# Within the calculator/ directory
$ rustc src/main.rs
$ ./main
Hello, world!
```

### Compile Project using **Cargo**

Run the following command in your terminal:

```bash
$ cargo build
```

This command instructs Cargo to compile your Rust code and its dependencies. By default, Cargo creates an optimized build for development in the **target/debug** directory.



**Build for Release:** To create a more optimized build suitable for production, use the --release flag:


```bash
$ cargo build --release
```

This creates the binary in the **target/release** directory.


use std::env::{args, Args};


fn main() {
    let mut args: Args = args(): //The args variable needs to be declared as mutable, because the nth method mutable iterates over the elements, and removes the element accessed.

     // The first argument is the location of the compiled binary, so skip it
    let first: String = args.nth(1).unwrap();
    // After accessing the second argument, the iterator's next element becomes the first


}
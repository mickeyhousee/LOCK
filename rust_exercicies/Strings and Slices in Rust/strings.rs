//A common point of confusion for beginner Rustacians is the difference between the String struct and the str type.


let my_str: &str = "Hello, world!";

let my_string: String = String::from("Hello, world!");

//In the above example, my_str is a reference to a string literal, and my_string is an instance of the String struct.
//An important distinction between the two is that my_str is stack stored, and my_string is heap allocated. This means my_str's value cannot change, and its size is fixed, whilst my_string can have an unknown size at compile time.
//The string literal is also known as a string slice. This is because a &str refers to part of a string. Generally, this is how arrays and strings are similar:

let my_string = String::from("The quick brown fox");
let my_str: &str = &my_string[4..9]; // "quick"

let my_arr: [usize; 5] = [1, 2, 3, 4, 5];
let my_arr_slice: &[usize] = &my_arr[0..3]; // [1, 2, 3]

//The [T; n] notation is used to create an array of n elements of type T.



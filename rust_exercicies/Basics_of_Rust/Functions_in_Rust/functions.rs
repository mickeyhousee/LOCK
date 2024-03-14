//You declare functions using the fn keyword:
fn main() {
    // This is a code comment
  }

//Functions return using the return keyword, and you need to explicitly specify the return type of a function, unless the return type is an empty tuple ():

fn main() -> () { // Unnecessary return type
    my_func();
  }
  
  fn my_func() -> u8 {
    return 0;
  }

//Functions also return an expression missing the semi-colon:

fn my_func() -> u8 {
    0
  }


//Function parameters are typed using the : syntax:


fn main() {
let _unused_variable = my_func(10);
}

fn my_func(x: u8) -> i32 {
x as i32
}

//The underscore before a variable name is a convention to indicate that the variable is unused. The as keyword asserts the type of the expression, provided the type conversion is valid.


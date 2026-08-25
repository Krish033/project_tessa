
class Person {

    [string] $Name
    [int] $Age

    Person([string] $Name, [int] $Age) {
        $this.Name = $Name
        $this.Age = $Age
    }

    [string]GetInfo() {
        return "$($this.Name) is $($this.Age) years old"
    }
}
    

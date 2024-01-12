# yo wassup autumn

## database formatting
### SETTINGS TABLE
|          | id  | active | banned | background | dmOnQuote | unlocks | customBg |
| -------- | --- | ------ | ------ | ---------- | --------- | ------- | -------- |
| primary  | ✅   |        |        |            |           |         |          |
| unique   | ✅   |        |        |            |           |         |          |
| not null | ✅   | ✅      | ✅      | ✅          | ✅         | ✅       |          |
| default  | -1  | 0      | 1      | "default"  | 0         | 0       | *NULL*   |

## background integer calculation
here's the table for background calculation
| Background | Integer | Binary Offset | Retrieval |
| ---------- | ------- | ------------- | --------- |
| Default    | 0       | N/A           | N/A       |
| Developer  | 1       | 1 << 0        | 1 >> 0    |
| Beta       | 2       | 1 << 1        | 1 >> 1    |
| Custom     | 4       | 1 << 2        | 1 >> 2    |

## How to get the integers
### Solution (in Python)

You can access the binary digit with index `n` (with the right-most digit having index `0`) of any number num using the following code:
```
digit = (num & (1 << n)) >> n
```
If you want this data as a string, you can add `digit = str(digit)` afterwards.
### Explanation
#### Filtering Numbers Using & ("bitwise and")

The `&` operation takes two binary numbers and gives back a third binary number with 1s only in those positions where both of the original numbers had 1s.

You can use this property to "fish out" (or "mask out") the value of any binary digit of any number. For example, if we wanted to figure out the value of the 4th binary digit of the number 51:
```
  1 1 0 0 1 1 (51 in binary)
& 0 1 0 0 0 0 (filter value - see below)
-------------
  0 1 0 0 0 0 (result)
```
The "filter" value above is a number that we build using our knowledge of which binary digit we want to check. Since we want the digit at index 4, we use a number consisting of all 0's, except for a 1 in the 4th position (again, counting from the right, and starting from 0).

Since our filter value only has a 1 in the 4th position, we know that our result will have 0s in every position except the 4th position. The 4th position could be a 0 or a 1, depending on the other number.

This is fine on paper, but how do we obtain the filter value based on the index? For this we use another bitwise operation: left shift.
#### Constructing A Filter Using << ("bitwise left shift")

The left shift operation essentially pads a number with a certain number of 0's on the right side. For example, here's `1 << 4`:
```
        1 (binary)
<<      4 (decimal)
---------
1 0 0 0 0 (binary)
``````
This gives us a way to construct the filter value using only the digit's index: If we want a number with a `1` in position `n`, and `0`s everywhere else, we can build it using `1 << n`.
#### Fixing The Result Using >> ("bitwise right shift")

Finally, we need to convert the result to either a `0` or a `1`. Since the value we "fish out" still has 0s on the right side (see the bitwise `&` computation above), its actual value is either `0` or `2 ** n`, not `0` or `1`.

To convert the value to a `0` or a `1`, we just right-shift (`>>`) the result by the index number (`n`):
```
   0 1 0 0 0 0 (binary)
>>           4 (decimal)
--------------
           0 1 (binary)
             1 (discard leading 0s)
```
Right shift does the opposite operation of left shift: it removes `0`s from the right side. The `0`s on the left side we can just discard, since they don't contribute to the number's value.
### Summary

An expanded form of the solution above could look like this:
```
filter = 1 << n
result = num & filter
digit = result >> n
```
Any time you're working with binary digits, consider using bitwise operations. They're really useful.

*(source: [here](https://stackoverflow.com/questions/49079440/access-an-element-of-a-binary-number-in-python))*
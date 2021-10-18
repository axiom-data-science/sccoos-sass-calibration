# Notes about Corrupted Data Files

## The problem

Perfect lines in these data files have a hash-mark `#` that separates the server info (time and IP) from the data.
A good line will look like:

```
2021-10-10T02:38:20Z,166.148.81.45,# 17.8714,  4.39094,    1.813, 0.2454, 0.0000, 0.0001, 0.0001,  33.4107, 10 Oct 2021 02:38:13,  24.0865, 13.7, 192.6
```

There are a million ways this perfection can be corrupted. Here are a few ...

``` 
2021-10-10T02:14:20Z,166.148.81.45,,    1.918, 0.3063, 0.0000, 0.0002, 0.0001,  33.4141, 10 Oct 2021 02:14:13,  24.0774, 13.8, 192.2
2021-10-10T02:18:20Z,166.148.81.45,��iʢ��b�rª�b�r�ʚ�b�r����b�r����b�r����b��r����b��z�с2021 02:18:13,  24.0801, 13.8, 192.6
2021-10-10T02:23:20Z,0.0.0.0,#
2021-10-10T22:58:20Z,166.148.81.45,�# 18.2001,  4.42358,    2.926, 0.2752, 0.0000, 0.0001, 0.0002,  33.4184, 10 Oct 2021 22:58:13,  24.0121, 13.8, 189.3
2021-10-10T23:02:20Z,166.148.81.45, 18.3912,  4.44245,    2.924, 0.2435, 0.0000, 0.0002, 0.0001,  33.4219, 10 Oct 2021 23:02:13,  23.9676, 13.8, 189.9
```

## The solution

The wide variation in contaminated lines means that it is hard to parse the good from the bad.  For instance,
some lines look OK except that they are just missing the `#`. But other lines are total goners. There
are even lines where gibberish is inserted into what looks like OK data.

Even worse, I can't be sure I've seen every bad permutation possible.

So I had to make some choices and assumptions:
0. Avoid ingesting bad data even at the risks of losing a few points.
1. If the IP is obviously bad, the data is also bad: remove the line
2. If there is no `#`, the beginning of the data cannot be determined: remove the line
3. If there is a gibberish character in the temperature field (bad line 4 above): filter to just digits and keep the line

Caveats

* In bad line 5 above, it looks like good data without `#`. Should I try and save that line?  No.
  * What if a digit was also dropped in addition to `#`?  In that (so far hypothetical) case, 5.0345 might look right, but it's really supposed to be 15.0345.    
* In some cases, it looks like some fields might be OK. 
  * Oh, but which ones?


## Converting to float
 
To convert temperature to a float, the `#` must be removed. Originally, I use this:
```      
data[start_column] = data[start_column].str.replace('#', '')
```
but then a Stearn's Whard file showed up with Issue #3. Instead, I had to brutally restrict to just digits:
```
data[start_column].replace(regex=True, inplace=True, to_replace=r'[^0-9.\-]', value=r'')
```


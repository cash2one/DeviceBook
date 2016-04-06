def foo(num,base):
    if(num>=base):
        foo(num/base,base)
    print num%base

foo(126,2)
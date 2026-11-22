def pulse(n):
    return int(2 <= n <= 5)

def delay(n, d):
    return pulse(n-d)

def reverse(n):
    return pulse(-n)

def energy(values):
    return sum(abs(x)**2 for x in values)

if __name__ == "__main__":
    assert [pulse(n) for n in range(8)] == [0,0,1,1,1,1,0,0]
    assert [delay(n,2) for n in range(10)][4:8] == [1,1,1,1]
    assert [reverse(n) for n in range(-6,1)][1:5] == [1,1,1,1]
    assert energy([1,-2,1]) == 6
    print("PASS: delay, reversal, discrete energy")

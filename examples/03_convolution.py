def convolve(x, h):
    """Full finite linear convolution with zero extension."""
    if not x or not h:
        return []
    y = [0]*(len(x)+len(h)-1)
    for i, a in enumerate(x):
        for j, b in enumerate(h):
            y[i+j] += a*b
    return y

if __name__ == "__main__":
    y = convolve([1,2,1], [1,1])
    assert y == [1,3,3,1]
    assert sum(y) == sum([1,2,1])*sum([1,1])
    assert convolve([1],[0.5,0.25]) == [0.5,0.25]
    print("PASS: finite linear convolution")

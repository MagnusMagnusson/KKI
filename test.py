def a(n):
	if(n <= 0):
		return 1;
	return b(n - 1) + c(n - 1, n -1)

def b(n):
	if n <= 0:
		return a(n-1)
	if n == 1:
		return c(1,n - 1)
	return b(n - 1)
def c(n,m):
	x = [x for x in range(50)]
	if(n <= 0):
		return a(n - 1) 
	if(m == 1):
		return 1
	if(m == 0):
		return c(1, n + 1)
	return a(n)




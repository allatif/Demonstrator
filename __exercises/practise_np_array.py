import numpy as np

A = np.array([2, 3, 4])
print(A)

B = np.arange(1, 12, 2)
print(B)

C = np.linspace(1, 12, 6)
print(C)

C = C.reshape(3, 2)
print(C)

print("Size of C:", C.size)
print("Shape of C:", C.shape)
print("Type:", C.dtype)
print("Byte:", C.itemsize)

D = np.array([(1.5, 2, 3), (4, 5, 6)])
print(D)
print(C < 4)

C *= 3
print(C)

Z = np.zeros((4, 3))
print(Z)

O_ = np.ones((4, 3))
print(O_)

E = np.array([2, 3, 4], dtype=np.int16)
print(E)
print("Byte:", E.itemsize)
print("Type:", E.dtype)

R = np.random.random((2, 3))
print(R)

np.set_printoptions(precision=2, suppress=True)
# suppress scientific notations
print(R)

Rint = np.random.randint(0, 10, 5)
print(Rint)
print("Sum:", Rint.sum())
print("Min:", Rint.min())
print("Max:", Rint.max())
print("Avrg:", Rint.mean())
print("Variance:", Rint.var())
print("Standard Deviation:", Rint.std())

Rint = np.random.randint(1, 10, 6)
Rint = Rint.reshape(3, 2)
print(Rint)
print("Sum of every row:", Rint.sum(axis=1))
print("Sum of every column:", Rint.sum(axis=0))
print("Standard Deviation by column:", Rint.std(axis=0))

data = np.loadtxt("data.txt", dtype=np.float16, delimiter=",", skiprows=1)
print(data)

T = np.arange(10)
print(T)
np.random.shuffle(T)
print(T)
cho = np.random.choice(T)
print(cho)

R_int = np.random.random_integers(5, 10, 2)
print(R_int)

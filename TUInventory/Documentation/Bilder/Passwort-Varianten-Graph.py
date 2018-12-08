import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

k = np.vectorize(lambda n: n*np.log(n))
n = np.linspace(0, 100, 250)
k = k(n)

plt.plot(k, n, label=r"$k = n \cdot ln(n)$")
plt.plot((15,), (77,), "o", label="Aktueller Stand")
plt.plot((15,), (84,), "o", label="Neuer Stand")
plt.xlabel("k - Länge des Passworts")
plt.ylabel("n - Anzahl an verfügbaren Zeichen")
plt.legend()
plt.grid()
plt.show()

####

k = np.linspace(0, 20, 10000)[1:]
n = np.linspace(0, 20, 10000)[1:]

range_ = [5]
for i, j in enumerate(range_):
    df_dk = np.vectorize(lambda k, n=j: k*n**(k-1))(k)
    df_dn = np.vectorize(lambda n, k=j: n**k*np.log(n))(n)

    plt.subplot(len(range_), 1, i+1).set_title(f"i = {j}")
    plt.semilogy(k, df_dk, label=r"$f_1 = \frac {\partial f} {\partial k} = k \cdot n ^{k-1} $")
    plt.semilogy(k, df_dn, label=r"$f_2 = \frac {\partial f} {\partial n} = n^k \cdot ln(n)$")
    plt.xlabel("k/n")
    plt.ylabel(r"$f_1(k) / f_2(n)$")
    plt.grid()
    plt.legend()

plt.show()

####

k_max = 100
k_i = 500
n_max = 30
n_i = 500
k = np.linspace(0, k_max, k_i)
n = np.linspace(0, n_max, n_i)[1:]
f = np.vectorize(lambda k, n: k*n**(k-1) - n**k*np.log(n))

print("started calc")
f = np.array([[f(K, N) for K in k] for N in n])
print("finished calc")
f = [[0 if i > 0 else 255 for i in row] for row in f]

print(np.shape(f))
plt.imshow(f, cmap="Greys", interpolation="quadric", origin="lower")
plt.xlabel("k")
plt.ylabel("n")
plt.xticks([i*k_i/k_max for i in range(0, k_max+1, 5)], [str(i) for i in range(0, k_max+1, 5)])
plt.yticks([i*n_i/n_max for i in range(0, n_max+1, 5)], [str(i) for i in range(0, n_max+1, 5)])
plt.grid()
plt.show()

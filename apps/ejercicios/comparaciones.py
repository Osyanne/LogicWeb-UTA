# apps/ejercicios/comparaciones.py
# Contenido curado para la pagina "Un problema, tres lenguajes".
# NO se ejecuta: es texto educativo que el estudiante lee.

PROBLEMAS = [
    {
        "slug": "par-impar",
        "titulo": "Es par o impar",
        "nivel": "Basico",
        "enunciado": "Leer un numero entero y mostrar si es par o impar.",
        "idea": "Un numero es par si el resto de dividirlo entre 2 es cero. El operador modulo (%) devuelve ese resto, y existe en los tres lenguajes.",
        "lenguajes": [
            {
                "id": "cpp", "label": "⚡ C++", "color": "#00599c",
                "codigo": """#include <iostream>      // entrada/salida
using namespace std;
int main() {
    int n;               // el tipo es obligatorio
    cin >> n;            // lee del teclado
    // ternario: condicion ? si : no
    cout << (n % 2 == 0 ? "Par" : "Impar");
    return 0;
}""",
                "como": "Declara el tipo (int), incluye <iostream> para cin/cout y resuelve con un operador ternario. Compila a binario nativo.",
            },
            {
                "id": "python", "label": "\U0001f40d Python", "color": "#3572a5",
                "codigo": """# input() lee texto; int() lo convierte
n = int(input())
# expresion condicional en una linea
print("Par" if n % 2 == 0 else "Impar")""",
                "como": "No declara tipos: int(input()) lee y convierte. Lo resuelve en 2 lineas con una expresion condicional. Es interpretado.",
            },
            {
                "id": "java", "label": "☕ Java", "color": "#b07219",
                "codigo": """import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();   // tipado estatico
        System.out.println(n % 2 == 0 ? "Par" : "Impar");
    }
}""",
                "como": "Todo vive dentro de una class y del metodo main. Usa Scanner para leer. Tipado estatico; corre sobre la JVM.",
            },
        ],
        "diferencias": [
            {"titulo": "Entrada/salida", "detalle": "C++ cin/cout, Python input()/print(), Java Scanner/System.out."},
            {"titulo": "Tipos", "detalle": "C++ y Java obligan a declararlos (int); Python los infiere solo."},
            {"titulo": "Estructura", "detalle": "Python va directo; C++ necesita main(); Java ademas exige una class."},
            {"titulo": "Concision", "detalle": "Python (2 lineas) es el mas corto; C++ y Java necesitan mas estructura."},
        ],
    },
    {
        "slug": "celsius-fahrenheit",
        "titulo": "Celsius a Fahrenheit",
        "nivel": "Basico",
        "enunciado": "Leer una temperatura en grados Celsius y mostrarla en Fahrenheit.",
        "idea": "La formula es F = C * 9/5 + 32. Cuidado: si dividis 9/5 con numeros enteros el resultado se trunca a 1; hay que trabajar con decimales.",
        "lenguajes": [
            {
                "id": "cpp", "label": "⚡ C++", "color": "#00599c",
                "codigo": """#include <iostream>
using namespace std;
int main() {
    double c;            // decimal, no int
    cin >> c;
    double f = c * 9.0 / 5 + 32;   // 9.0 fuerza division real
    cout << f;
}""",
                "como": "Usa double para no truncar. Con 9.0/5 fuerza la division decimal: si fuera 9/5 con enteros daria 1.",
            },
            {
                "id": "python", "label": "\U0001f40d Python", "color": "#3572a5",
                "codigo": """c = float(input())   # float, no int
# en Python 3, '/' siempre da decimal
f = c * 9 / 5 + 32
print(f)""",
                "como": "float(input()) lee un decimal. En Python 3 el operador / siempre devuelve decimal, asi que 9/5 ya es 1.8.",
            },
            {
                "id": "java", "label": "☕ Java", "color": "#b07219",
                "codigo": """import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        double c = new Scanner(System.in).nextDouble();
        double f = c * 9.0 / 5 + 32;
        System.out.println(f);
    }
}""",
                "como": "nextDouble() lee el decimal. Como en C++, conviene 9.0/5 para evitar la division entera.",
            },
        ],
        "diferencias": [
            {"titulo": "Tipos numericos", "detalle": "C++ y Java declaran double; Python infiere el float."},
            {"titulo": "Division", "detalle": "En C++/Java 9/5 con enteros trunca a 1 (usar 9.0/5); en Python 3 / ya es decimal."},
            {"titulo": "Lectura", "detalle": "cin>>c (C++), nextDouble() (Java), float(input()) (Python)."},
        ],
    },
    {
        "slug": "factorial",
        "titulo": "Factorial",
        "nivel": "Medio",
        "enunciado": "Leer un numero n y calcular su factorial (n! = 1 * 2 * ... * n).",
        "idea": "Se multiplica un acumulador por cada numero de 1 a n con un bucle. El factorial crece muy rapido y puede desbordar los enteros de tamano fijo.",
        "lenguajes": [
            {
                "id": "cpp", "label": "⚡ C++", "color": "#00599c",
                "codigo": """#include <iostream>
using namespace std;
int main() {
    int n;
    cin >> n;
    long long fact = 1;            // long long: numeros grandes
    for (int i = 1; i <= n; i++)
        fact *= i;
    cout << fact;
}""",
                "como": "for clasico (i de 1 a n) acumulando el producto. Usa long long porque el factorial desborda un int rapido.",
            },
            {
                "id": "python", "label": "\U0001f40d Python", "color": "#3572a5",
                "codigo": """n = int(input())
fact = 1
for i in range(1, n + 1):   # range(1, n+1) = 1..n
    fact *= i
print(fact)""",
                "como": "range(1, n+1) genera 1..n. Los enteros de Python no tienen limite de tamano, asi que nunca desbordan.",
            },
            {
                "id": "java", "label": "☕ Java", "color": "#b07219",
                "codigo": """import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        int n = new Scanner(System.in).nextInt();
        long fact = 1;             // long: numeros grandes
        for (int i = 1; i <= n; i++)
            fact *= i;
        System.out.println(fact);
    }
}""",
                "como": "Mismo for que C++. Usa long para numeros grandes; aun asi tiene un limite (a diferencia de Python).",
            },
        ],
        "diferencias": [
            {"titulo": "El bucle", "detalle": "C++/Java: for(int i=1; i<=n; i++). Python: for i in range(1, n+1)."},
            {"titulo": "Limite de los enteros", "detalle": "C++/Java desbordan (long llega mas lejos que int); los int de Python son ilimitados."},
            {"titulo": "Tipos", "detalle": "C++/Java declaran el tipo del acumulador; Python lo infiere."},
        ],
    },
    {
        "slug": "bubble-sort",
        "titulo": "Bubble Sort",
        "nivel": "Avanzado",
        "enunciado": "Ordenar un arreglo de menor a mayor comparando e intercambiando elementos vecinos.",
        "idea": "Se recorre el arreglo varias veces; en cada pasada se comparan elementos vecinos y se intercambian si estan en desorden. Son dos bucles anidados.",
        "lenguajes": [
            {
                "id": "cpp", "label": "⚡ C++", "color": "#00599c",
                "codigo": """#include <iostream>
using namespace std;
int main() {
    int a[] = {5, 2, 9, 1};
    int n = 4;
    for (int i = 0; i < n - 1; i++)
        for (int j = 0; j < n - 1 - i; j++)
            if (a[j] > a[j + 1])
                swap(a[j], a[j + 1]);   // intercambio
    for (int i = 0; i < n; i++) cout << a[i] << " ";
}""",
                "como": "Arreglo de tamano fijo. swap() intercambia dos elementos. El for interno acorta con -i: los mayores ya quedaron al final.",
            },
            {
                "id": "python", "label": "\U0001f40d Python", "color": "#3572a5",
                "codigo": """a = [5, 2, 9, 1]
n = len(a)
for i in range(n - 1):
    for j in range(n - 1 - i):
        if a[j] > a[j + 1]:
            # swap pythonico en una linea
            a[j], a[j + 1] = a[j + 1], a[j]
print(a)""",
                "como": "Usa una lista (len(a)). El intercambio se hace en una sola linea, sin variable temporal: a[j], a[j+1] = a[j+1], a[j].",
            },
            {
                "id": "java", "label": "☕ Java", "color": "#b07219",
                "codigo": """import java.util.Arrays;
public class Main {
    public static void main(String[] args) {
        int[] a = {5, 2, 9, 1};
        int n = a.length;
        for (int i = 0; i < n - 1; i++)
            for (int j = 0; j < n - 1 - i; j++)
                if (a[j] > a[j + 1]) {
                    int t = a[j];          // swap con temporal
                    a[j] = a[j + 1];
                    a[j + 1] = t;
                }
        System.out.println(Arrays.toString(a));
    }
}""",
                "como": "int[] con .length. El intercambio necesita una variable temporal. Arrays.toString() imprime la lista completa.",
            },
        ],
        "diferencias": [
            {"titulo": "Arreglos", "detalle": "C++ int a[] y Java int[] son de tamano fijo (n, a.length); Python usa una lista dinamica (len(a))."},
            {"titulo": "Intercambio (swap)", "detalle": "Python lo hace en una linea (a, b = b, a); C++ con swap(); Java necesita una variable temporal."},
            {"titulo": "Imprimir", "detalle": "C++ recorre con un for; Python print(a); Java Arrays.toString(a)."},
        ],
    },
]

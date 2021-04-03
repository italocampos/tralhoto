# Tralhoto

Tralhoto is a MAS modeled as a evaluative activity for the Multi-Agent System
subject of the Programa de Pós-Graduação em Ciência da Computação from
Faculdade de Computação, UFPA.

This SMA deals was modeled to simulate and reduce the time of the trips for the
BRT bus system in the city of Belém-PA, Brazil.


## How it works?

To understand how this system works, please, refer to the paper in [this link](https://github.com/italocampos/tralhoto/blob/main/docs/paper.pdf) 
(Brazilian Portuguese only).


## Installation and dependencies

This system is written to work with [PADE](https://github.com/italocampos/pade).
Note that this version of PADE is a fork. To see the original project, follow
[this link](https://github.com/grei-ufc/pade).

This software depends on the following tools:

- [PADE](https://github.com/italocampos/pade);
- [Color](https://github.com/italocampos/color);
- [Scipy](https://www.scipy.org/);


### Running the simulations


After installed the referred dependencies, clone this repository in your
workspace by running:

``` shell
git clone https://github.com/italocampos/tralhoto
```

Now you can run the simulations of this SMA with PADE following the command
below.

``` shell
cd tralhoto/
pade start-runtime main.py
```

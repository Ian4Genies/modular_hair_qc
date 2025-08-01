# Directory Structure Documentation

This document demonstrates best practices for representing directory structures in markdown format.

## Basic Tree Structure

The most common way to represent a directory structure uses tree-like ASCII characters:

```
modular_hair/
├── module/
│   ├── scalp/
│   │   ├── scalp.usd
│   │   ├── alpha/
│   │   │   ├── fade/
│   │   │   │   ├── lineUp.png
│   │   │   │   ├── midFade.png
│   │   │   ├── hairline/
│   │   │   ├── sideburn/
│   │   ├── normnal/
│   │   │   ├── ripple.png
│   │   │   ├── wavy.png
│   ├── crown/
│   │   ├── short_crown_smallAfro.usd
│   │   ├── short_crown_medAfro.usd
│   │   ├── short_crown_slicked.usd
│   │   ├── short_crown_combed.usd
│   │   ├── Long_crown_simple.usd
│   │   ├── Long_crown_braided.usd
│   │   ├── Long_crown_fancy.usd
│   └── tail/
│   │   ├── long_tail_braided.usd
│   │   ├── long_tail_pony.usd
│   │   ├── long_tail_beaded.usd
│   └── bang/
│   │   ├── long_bang_straightCut.usd
│   │   ├── long_bang_messy.usd
│   │   ├── long_bang_parted.usd
├── style/
│   ├── short_medAfro.usd
│   ├── long_braided_beaded_messy.usd
│   ├── long_braided_braided_straightCut.usd
│   ├── long_simple_pony_parted.usd
├── Group/
│   ├── short.usd
│   ├── long.usd
├── data/
│   ├── Cross-Module_Exclusion_Log.json
└── README.md
```

## File Naming Conventions

### module
`<group>_<module>_<name>.usd
### style
`<group>_<crown_name>_<tail_name>_<bang_name>.usd`


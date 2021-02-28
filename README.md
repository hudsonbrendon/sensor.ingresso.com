![hacs_badge](https://img.shields.io/badge/hacs-custom-orange.svg) [![BuyMeCoffee][buymecoffeebedge]][buymecoffee]



# ingresso.com Sensor Component

![logo.jpg](logo.png)

Custom component to get movie information in your city available at ingresso.com for the home assistant

# Installation

## HACS

- Have [HACS](https://hacs.xyz/) installed, this will allow you to easily update.

- Add https://github.com/hudsonbrendon/sensor.ingresso.com as a custom repository with Type: Integration
- Click Install under "Ingresso.com" integration.
- Restart Home-Assistant.

## Manual

- Copy directory custom_components/ingresso to your <config dir>/custom_components directory.
- Configure.
- Restart Home-Assistant.

# Configuration

```yaml
- platform: ingresso
  city_id: your-city-id
  city_name: your-city-name
  partnership: your-partnership
```

Some of the partnerships are: cinepolis, cinemark, moviecom, playarte ...

### Example:

```yaml
- platform: ingresso
  city_id: 48
  city_name: Natal
  partnership: cinepolis
```

## Get your city id

Access the url below with your UF see your city_id in the list of cities in your state.

https://api-content.ingresso.com/v0/states/YOUR-UF

UFs table:
| UF        | Estate  |
| --------- |:-----:|
| AC      | Acre |
| AL      | Alagoas |
| AP      | Amapá |
| AM      | Amazonas |
| BA      | Bahia |
| CE      | Ceará |
| DF      | Distrito Federal |
| ES      | Espírito Santo |
| GO      | Goiás |
| MT      | Mato Grosso |
| MA      | Maranhão |
| MS      | Mato Grosso do Sul |
| MG      | Minas Gerais |
| PA      | Pará |
| PB      | Paraíba |
| PR      | Paraná |
| PE      | Pernambuco |
| PI      | Piauí |
| RJ      | Rio de Janeiro |
| RN      | Rio Grande do Norte |
| RS      | Rio Grande do Sul |
| RO      | Rondônia |
| RR      | Roraima |
| SC      | Santa Catarina |
| SP      | São Paulo |
| SE      | Sergipe |
| TO      | Tocantins |

### Example:

https://api-content.ingresso.com/v0/states/SP

# Debugging

```yaml
logger:
  default: info
  logs:
    custom_components.ingresso: debug
```

[buymecoffee]: https://www.buymeacoffee.com/hudsonbrendon
[buymecoffeebedge]: https://camo.githubusercontent.com/cd005dca0ef55d7725912ec03a936d3a7c8de5b5/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6275792532306d6525323061253230636f666665652d646f6e6174652d79656c6c6f772e737667

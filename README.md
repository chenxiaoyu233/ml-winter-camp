# Avalible model
| name | description                   | accuracy |
| --   | ---                           | --       |
| cnn  | cnn+maxpool+cnn+maxpool+dense | 75%      |
| lstm | lstm+lstm+dense               |          |


# csv column
|name | description|
|-----|------------|
|type| 16 types|
|posts| long sentence, maxlength=2312|
|IE | I=1,E=0 |
|NS | N=1,S=0 |
|TF | T=1,F=0 |
|JP | J=1,P=0 |
___
# csv version
| name       | description                 |
| ------     | ----                        |
| MTBIv0.csv | original csv                |
| MTBIv1.csv | one entry for each person   |
| MTBIv2.csv | one entry for each sentence |

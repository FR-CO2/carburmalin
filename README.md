# Carburmalin

## Vie privée
Ce projet a pu objectif d'être utile à tous, dans le respect de la vie privée.
Nous ne récoltons pas d'informations sur vous autres que les recherches que vous faites (ville, code postale, station service, carburant). 

Nous ne vendons aucune information à qui que ce soit.

## Remonté d'anomalie ou proposition d'évolution
### Anomalie
Si vous rencontrez des anomalies sur le [site internet](https://carburmalin.fr) ou sur l'application [Android](https://play.google.com/store/apps/details?id=fr.carburmalin.apk), vous pouvez créer un ticket afin que nous le résolvons.
Pour cela, il suffit d'aller sur l'onglet Issue, créer une nouvelle Issue. Merci de préciser dans le label "bug" et de commencer le titre par [WEB] ou [APPLI], afin que nous sachions sur quel environnement se trouve l'anomalie.
### Evolution
Si vous ailmeriez faire une nouvelle fonctionnalité, n'hésitez pas à nous en faire par par le même biais que les anomalies, mais en mettant le label "enhancement" et [WEB] ou [APPLI] pour savoir sur quel environnement ça devrait être fait.
Toutes les demandes d'évolutions ne pourront être prises en compte et nous ferons le choix dans celles qui seront intégrées par la suite. Si nous jugeons qu'une demande d'évolution ne sera pas utile ou contraire aux valeurs que nous portons, nous nous réservons le droit de ne pas la développer.
Nous essayerons de vous tenir au courant de l'évolution dans le ticket correspondant.
## FuelPred : Prédiction du carburant

Cette partie comporte les différentes IA utilisées dans le projet [web](https://carburmalin.fr) et pour l'application [Android](https://play.google.com/store/apps/details?id=fr.carburmalin.apk) Carburmalin.

Elle comporte plusieurs IA pour prédire les variations des prix :
* du pétrole
* des moyennes de chaque département
* de chaque type de carburant pour chaque station service
* et une qui va calculer directement les moyennes du département et le prix de chaque type de carburant pour chaque station service. Elle ne prend pas en compte le prix du pétrole.

Les IA sont divisées en deux familles : 
* celles d'entrainements des IA (les train)
* et celles d'utilisation des IA entrainées (les predict)

Elles tournent avec du Python 3.6 et tensorflow.

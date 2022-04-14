from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast

# -- Begin initialisatie app --
app = Flask(__name__)
api = Api(app)

# -- Einde initialisatie app --

# -- Begin Endpoints --
# Voor elke 'endpoint' maken we een Class
# /temperatuur
temperatuur_path = './data/celsius.csv'
# /decibel
decibel_path = './data/decibel.csv'

class Temperatuur(Resource):
    # Klasse voor /Temperatuur endpoint

    def get(self):
        """Wanneer er op de endpoint een HTTP GET request binnenkomt,
        zal de client het celsius.csv bestand te zien krijgen in JSON.
        """
        # Zet data als temperatuur csv bestand
        data = pd.read_csv(temperatuur_path)
        data = data.to_dict()
        return {'data': data}, 200

    def post(self):
        """ Wanneer er een post request komt op dit endpoint, zal er een device dus zijn temperatuur willen posten op de API.
        Deze request moeten we opvangen en de data opslaan op de API.
        """
        # Definieer onze parser
        parser = reqparse.RequestParser()

        # Argumenten die een post request moet bevatten, userid, celsius en tijd
        # Een post request zal er dan zo uit zien: 127.0.0.1:5000/temperatuur?userid=4&celsius=25&tijd=15:55:30
        parser.add_argument('userid', required=True, type=int)
        parser.add_argument('celsius', required=True, type=float)
        parser.add_argument('tijd', required=True, type=str)
        args = parser.parse_args()

        # Zet data als locatie van de temperatuur csv file
        data = pd.read_csv(temperatuur_path)

        # Append de data van de post request
        data = data.append({
            'userid': args['userid'],
            'celsius': args['celsius'],
            'tijd': args['tijd']
        }, ignore_index=True)

        data.to_csv(temperatuur_path, index=False)
        return {'data': data.to_dict()}, 200
    
    def delete(self):
        """
        Dit is de functie die delete requestst opvangt. We willen namelijk niet een history van duizenden rijen.
        Daarom is het verstandig om af en toe de data te verwijderen. Bijvoorbeeld voor 01-01-2022.
        """

        # We definiëren een secret_key voor het verwijderen van data. Die mogen gebruikers natuurlijk nooit te weten komen.
        secret_key = 'Ikwilietsverwijderen'

        parser = reqparse.RequestParser()
        parser.add_argument('secret', required=True, type=str)
        parser.add_argument('tijdstip', required=True, type=str)
        args = parser.parse_args()

        # Als secret niet gelijk staat aan secret_key, weiger de request.
        if args['secret'] != secret_key:
            return {
                'message': "Error"
            }, 409
        
        data = pd.read_csv(temperatuur_path)
        tijdstip = args['tijdstip']

        # Als tijdstip niet aanwezig is in data['tijd'], dan is de request al klaar en hoeft er niks te gebeuren.
        tijden = []
        for i in data['tijd']:
            tijden.append(i)

        if tijdstip not in tijden:
            return {
                'message': "Tijdstip niet in lijst, klaar"
            }, 200
        
        # Verwijder alle rijen die 'tijdstip' als tijd hebben.
        data = data[data['tijd'] != args['tijdstip']]

        data.to_csv(temperatuur_path, index=False)
        return {'data': data.to_dict()}, 200

class Decibel(Resource):
    # Decibel werkt hetzelfde als temperatuur, maar is een andere endpoint :)
    pass


# -- Einde Endpoints --

# Voeg endpoints toe aan api (www.test.com/temperatuur)
api.add_resource(Temperatuur, '/temperatuur')
api.add_resource(Decibel, '/decibel')

if __name__ == '__main__':
    app.run(debug=True)

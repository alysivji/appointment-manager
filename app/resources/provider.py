from flask_restful import Resource
from webargs import fields
from webargs.flaskparser import use_args

from app import db, Provider
from app.config import BASE_URL
from app.schemas import ProviderSchema


# Configure reading from requests
PROVIDER_SCHEMA_POST = {
  'first_name': fields.Str(locations='json', required=True),
  'last_name': fields.Str(locations='json', required=True),
}

# Configure serializing models to JSON for response
provider_list_schema = ProviderSchema(many=True)
provider_schema = ProviderSchema()


class ProvidersResource(Resource):
    def get(self):
        all_providers = Provider.query.all()
        result = provider_list_schema.dump(all_providers)
        return result.data, 200

    @use_args(PROVIDER_SCHEMA_POST)
    def post(self, args):
        new_provider = Provider(first_name=args['first_name'],
                                last_name=args['last_name'])

        db.session.add(new_provider)
        db.session.commit()

        HEADERS = {
            'Location': f'{BASE_URL}/providers/{new_provider.id}',
        }

        return {}, 201, HEADERS


class ProvidersItemResource(Resource):
    def get(self, provider_id):
        provider = Provider.query.filter(Provider.id == provider_id).all()
        if len(provider) == 0:
            return None, 404

        result = provider_schema.dump(provider[0])
        return result.data, 200

    def delete(self, provider_id):
        provider = Provider.query.filter(Provider.id == provider_id).all()
        if len(provider) == 0:
            return None, 404

        db.session.delete(provider[0])
        db.session.commit()
        return None, 204

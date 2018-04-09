from flask_restful import Resource
from webargs import fields
from webargs.flaskparser import use_args

from app import app, db, Provider
from app.schemas import ProviderSchema
from app.utils import create_response, getitem_or_404

###############
# Configuration
###############

BASE_URL = app.config.get('BASE_URL')

# Configure reading from requests
PROVIDER_SCHEMA_POST = {
  'first_name': fields.Str(required=True),
  'last_name': fields.Str(required=True),
}

# Configure serializing models to JSON for response
provider_list_schema = ProviderSchema(many=True)
provider_schema = ProviderSchema()


###########
# Resources
###########

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

        return create_response(status_code=201, headers=HEADERS, data={})


class ProvidersItemResource(Resource):
    def get(self, provider_id):
        provider = getitem_or_404(Provider, Provider.id, provider_id)
        result = provider_schema.dump(provider)
        return create_response(status_code=200, data=result.data)

    def delete(self, provider_id):
        provider = getitem_or_404(Provider, Provider.id, provider_id)
        db.session.delete(provider)
        db.session.commit()
        return create_response(status_code=204, data={})

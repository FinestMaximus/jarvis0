
from pytm import (
    TM,
    Actor,
    Boundary,
    Classification,
    Data,
    Dataflow,
    Datastore,
    Server,
    DatastoreType,
)

tm = TM("API Backend Services TM")
tm.description = "This threat model describes an API interfacing with various backend services. It shows user interaction to the API, with data flow through the backend services and databases. It aims to identify potential security threats across the architecture."
tm.isOrdered = True
tm.mergeResponses = True
tm.assumptions = [
    "Assumes all services are hosted in a secured environment.",
    "Assumes that all data is encrypted in transit.",
]

internet = Boundary("Internet")
backend_services = Boundary("Backend Services")
backend_services.levels = [2]

user = Actor("User")
user.inBoundary = internet
user.levels = [2]

api_server = Server("API Server")
api_server.OS = "Ubuntu"
api_server.controls.isHardened = True
api_server.controls.sanitizesInput = True
api_server.controls.encodesOutput = True
api_server.controls.authorizesSource = True
api_server.sourceFiles = ["api_service/main.py"]

service_db = Datastore("Service Database")
service_db.OS = "PostgreSQL"
service_db.controls.isHardened = True
service_db.inBoundary = backend_services
service_db.type = DatastoreType.SQL
service_db.inScope = True
service_db.maxClassification = Classification.RESTRICTED

identity_service = Server("Identity Verification Service")
identity_service.OS = "CentOS"
identity_service.controls.isHardened = True
identity_service.inBoundary = backend_services

user_request_data = Data(
    "User Request and Data", classification=Classification.SECRET
)
user_to_api = Dataflow(user, api_server, "User sends request to API")
user_to_api.protocol = "HTTPS"
user_to_api.dstPort = 443
user_to_api.data = user_request_data
user_to_api.note = "Securely sends user data to the API"

api_to_service_db = Dataflow(api_server, service_db, "API communicates with Service DB")
api_to_service_db.protocol = "PostgreSQL"
api_to_service_db.dstPort = 5432
api_to_service_db.data = user_request_data
api_to_service_db.note = "API queries the Service Database"

service_response_data = Data(
    "Response from Service", classification=Classification.PUBLIC
)
service_db_to_api = Dataflow(service_db, api_server, "Service DB response to API")
service_db_to_api.protocol = "PostgreSQL"
service_db_to_api.dstPort = 5432
service_db_to_api.data = service_response_data
service_db_to_api.note = "Service database responds back to API"

api_to_user = Dataflow(api_server, user, "API returns response to User")
api_to_user.protocol = "HTTPS"
api_to_user.dstPort = 443
api_to_user.data = service_response_data
api_to_user.note = "API sends the response to the user"

if __name__ == "__main__":
    tm.process()

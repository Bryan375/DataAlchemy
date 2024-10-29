from typing import Dict, Optional
from rest_framework.response import Response
from rest_framework import status

class APIResponse:
    @staticmethod
    def success(data: Optional[Dict] = None, message: str = "Success", status_code: int = status.HTTP_200_OK) -> Response:
        response_data = {
            "status": "success",
            "data": data or {},
            "message": message,
            "code": status_code
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def error(message: str = "Error occurred", errors: Optional[Dict] = None,
              status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
        response_data = {
            "status": "error",
            "message": message,
            "errors": errors or {},
            "code": status_code
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def paginated_response(data: Dict, message: str = "Success",
                          status_code: int = status.HTTP_200_OK) -> Response:
        response_data = {
            "status": "success",
            "data": data.get("results", []),
            "message": message,
            "code": status_code,
            "pagination": {
                "count": data.get("count", 0),
                "next": data.get("next"),
                "previous": data.get("previous"),
                "current_page": data.get("current_page", 1),
                "total_pages": data.get("total_pages", 1),
                "page_size": data.get("page_size", 10)
            }
        }
        return Response(response_data, status=status_code)
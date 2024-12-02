import base64
import os
import json
import tempfile
import logging
from django.contrib import messages
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import PropertyForm
from aws_utility_library_roshinswebapp import *
# from aws_library.lambda_utils import invoke_lambda
# from aws_library.dynamodb_utils import store_an_item, get_property, scan_table
# from aws_library.s3_utils import upload_file
# from aws_library.sns_utils import publish_to_sns
# from aws_library.sqs_utils import receive_from_sqs, delete_from_sqs

    
class Properties(TemplateView):
    """View all properties with search functionality"""
    template_name = "properties/properties.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '').strip()  # Retrieve and clean the search query
        
        try:
            # Fetch properties from DynamoDB
            properties = scan_table(
                region=os.environ['AWS_REGION'],
                table_name=os.environ['DYNAMODB_TABLE_NAME']
            )

            # Add S3 image URLs for each property
            for property in properties:
                if "image_key" in property and property["image_key"]:
                    property["image_url"] = f"https://{os.environ['S3_BUCKET_NAME']}.s3.{os.environ['AWS_REGION']}.amazonaws.com/{property['image_key']}"
                else:
                    property["image_url"] = None

            # Filter properties based on the search query
            if search_query:
                properties = [
                    prop for prop in properties
                    if search_query.lower() in prop.get('title', '').lower() or
                       search_query.lower() in prop.get('location', '').lower() or
                       search_query.lower() in prop.get('description', '').lower()
                ]

            context["properties"] = properties
            context["search_query"] = search_query

        except Exception as e:
            # Log and handle errors gracefully
            context["properties"] = []
            context["error"] = f"Failed to load properties: {str(e)}"
        
        return context


class Propertydetail(TemplateView):
    """ Detail view of the property """
    template_name = "properties/property_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_id = self.kwargs.get('property_id')  # Retrieve property_id from the URL
        if property_id:
            try:
                # Fetch property details from DynamoDB
                property_data = get_property(
                    os.environ['AWS_REGION'],
                    os.environ['DYNAMODB_TABLE_NAME'],
                    property_id
                )
                context['property'] = property_data
                context['property_id'] = property_id 
                context["s3bucket"] = os.environ['S3_BUCKET_NAME']
            except Exception as e:
                context['error'] = f"Error fetching property details: {str(e)}"
        else:
            context['error'] = "Property ID not provided."
        return context

    def post(self, request, *args, **kwargs):
        property_id = kwargs.get('property_id')  # Retrieve property_id from the URL
        message = f"User {request.user.username} has requested a viewing for property ID {property_id}."

        try:
            # Publish the message to the SNS topic
            publish_to_sns(
                region=os.environ['AWS_REGION'],
                topic_arn=os.environ['SNS_TOPIC_ARN'],
                message=message
            )
        except Exception as e:
            return JsonResponse({'error': f"Failed to send SNS message: {str(e)}"}, status=500)

        # Redirect to the properties page
        return redirect('properties')


class Addproperty(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "properties/add_properties.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PropertyForm()
        return context

    def post(self, request, *args, **kwargs):
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            image = request.FILES.get("image")

            try:
                # Handle image upload
                image_key = None
                if image:
                    # Temporarily save the file to disk
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        for chunk in image.chunks():
                            temp_file.write(chunk)
                        temp_file_path = temp_file.name

                    # S3 object key
                    image_key = f"properties/{data['title'].replace(' ', '_')}.jpg"
                    print(f"Uploading image with key: {image_key}")
                    
                    # Upload the file using the existing function
                    success = upload_file(
                        file_name=temp_file_path,  # Pass the temporary file path
                        bucket=os.environ['S3_BUCKET_NAME'],
                        object_key=image_key,
                        extra_args={"ContentType": image.content_type}
                    )

                    # Remove the temporary file
                    os.remove(temp_file_path)

                    if not success:
                        raise Exception("Image upload to S3 failed.")

                # Store property in DynamoDB
                store_an_item(
                    region=os.environ['AWS_REGION'],
                    table_name=os.environ['DYNAMODB_TABLE_NAME'],
                    item={
                        "property_id": data["title"].replace(" ", "_"),
                        "title": data["title"],
                        "description": data["description"],
                        "price": str(data["price"]),
                        "property_type": data["property_type"],
                        "location": data["location"],
                        "bedrooms": data.get("bedrooms"),
                        "bathrooms": data.get("bathrooms"),
                        "area": str(data.get("area")),
                        "image_key": image_key or "no_image",  # Default to 'no_image' if no file is uploaded
                    }
                )

                # Redirect to the properties list
                return redirect("properties")
            except Exception as e:
                print(f"Error: {e}")
                return render(request, self.template_name, {
                    "form": form,
                    "error": f"An error occurred: {str(e)}"
                })
        else:
            print("Form errors:", form.errors)
            return render(request, self.template_name, {"form": form})

class Editproperty(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "properties/edit_properties.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_id = self.kwargs.get("property_id")

        if property_id:
            try:
                # Fetch property details for pre-filling the form
                property_data = get_property(
                    os.environ["AWS_REGION"],
                    os.environ["DYNAMODB_TABLE_NAME"],
                    property_id,
                )
                context["form"] = PropertyForm(initial=property_data)
            except Exception as e:
                logging.error(f"Error fetching property details: {e}")
                context["error"] = f"Failed to fetch property details: {str(e)}"
                context["form"] = PropertyForm()
        else:
            context["form"] = PropertyForm()

        return context

    def post(self, request, *args, **kwargs):
        form = PropertyForm(request.POST, request.FILES)
        property_id = self.kwargs.get("property_id")

        if form.is_valid():
            data = form.cleaned_data
            image = request.FILES.get("image")

            try:
                # Prepare Lambda payload
                object_key = f"properties/{data['title'].replace(' ', '_')}.jpg"
                payload = {
                    "operation": "update",
                    "table_name": os.environ["DYNAMODB_TABLE_NAME"],
                    "property_id": property_id,
                    "update_data": {
                        "price": str(data["price"]),
                        "description": data["description"],
                        "property_type": data["property_type"],
                        "location": data["location"],
                        "bedrooms": data.get("bedrooms"),
                        "bathrooms": data.get("bathrooms"),
                        "area": str(data.get("area")),
                    },
                    "bucket_name": os.environ["S3_BUCKET_NAME"],
                    "object_key": object_key,
                }
                if image:
                   image.seek(0)  # Reset the file pointer to the beginning
                   payload["new_image_file"] = base64.b64encode(image.read()).decode("utf-8")
                else:
                   logging.warning("No image provided for the update")


                # Invoke Lambda
                response = invoke_lambda(
                    function_name="update_property_function",  # Lambda function name
                    payload=payload,
                    region=os.environ["AWS_REGION"],
                )

                # Check Lambda response
                if response.get("statusCode") == 200:
                    logging.info("Property updated successfully via Lambda.")
                    return redirect("properties")
                else:
                    logging.error(f"Lambda error: {response.get('message')}")
                    raise Exception(response.get("message", "Unknown error during Lambda execution"))

            except Exception as e:
                # Log error and show error message
                logging.error(f"Error updating property: {e}")
                return render(request, self.template_name, {
                    "form": form,
                    "error": f"An error occurred while updating the property: {e}",
                })

        # If form is invalid, render the form with error messages
        return render(request, self.template_name, {"form": form, "error": "Invalid form submission."})

class Deleteproperty(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "properties/delete_properties.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        property_id = self.kwargs.get("property_id")  
        image_key = f"properties/{property_id}.jpg"

        try:
            # Invoke Lambda for deletion
            response = invoke_lambda(
                region=os.environ['AWS_REGION'],
                function_name="delete_property_function",
                payload={
                    "operation": "delete",
                    "table_name": os.environ['DYNAMODB_TABLE_NAME'],
                    "property_id": property_id,
                    "bucket_name": os.environ['S3_BUCKET_NAME'],
                    "object_key": image_key
                }
            )

            # Parse the Lambda response
            if response.get("statusCode") == 200:
                messages.success(request, "Property deleted successfully.")
            else:
                messages.error(request, f"Failed to delete property: {response.get('message')}")
        except Exception as e:
            
            messages.error(request, "An unexpected error occurred during deletion.")

        return redirect("properties")


class NotificationsPageView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "properties/notifications.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve messages from the SQS queue
        messages = receive_from_sqs(
            region=os.environ['AWS_REGION'],
            queue_url=os.environ['SQS_QUEUE_URL']
        )

        # Parse and format messages
        context["notifications"] = []
        for msg in messages:
            try:
                # Parse the message body as JSON
                body = json.loads(msg["Body"])
                context["notifications"].append({
                    "message": body.get("Message", "Unknown message"),
                    "timestamp": body.get("Timestamp", "Unknown timestamp"),
                    "receipt_handle": msg["ReceiptHandle"]
                })
            except json.JSONDecodeError:
                # If parsing fails, fallback to raw body
                context["notifications"].append({
                    "message": msg["Body"],
                    "timestamp": "Unknown timestamp",
                    "receipt_handle": msg["ReceiptHandle"]
                })

        return context
   
class DeleteNotificationView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        receipt_handle = request.POST.get("receipt_handle")
        if not receipt_handle:
            return JsonResponse({"success": False, "error": "Receipt handle not provided"}, status=400)

        try:
            # Delete the message from SQS
            delete_from_sqs(
                region=os.environ['AWS_REGION'],
                queue_url=os.environ['SQS_QUEUE_URL'],
                receipt_handle=receipt_handle
            )
            return redirect("notifications")
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)


    
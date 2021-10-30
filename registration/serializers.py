from django.db import models
from django.db.models import fields
from registration.models import Person
from rest_framework import serializers


class SiblingsSerializer(serializers.ModelSerializer):

    """
        Serializer to get siblings details of a person.
    """

    class Meta:
        model = Person
        fields = (
            "username",
            "id",
        )


class ParentSerializer(serializers.ModelSerializer):

    """
        Serializer to get parent details of a person.
    """

    class Meta:
        model = Person
        fields = (
            "username",
            "id",
        )


class CousinsSerializer(serializers.ModelSerializer):

    """
        Serializer to get cousins details of a person.
    """

    class Meta:
        model = Person
        fields = ("username", "id")


class PersonDataSerializer(serializers.ModelSerializer):

    """
        Serializer to get person details.
    """

    parent = ParentSerializer(many=True)
    siblings = SiblingsSerializer(many=True)

    class Meta:
        model = Person
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "birth_date",
            "siblings",
            "parent",
        )


class PersonRegistrationSerializer(serializers.ModelSerializer):

    """
        Serializer to register a person.
    """

    email = serializers.EmailField(max_length=50, required=True)
    password = serializers.CharField(max_length=150, write_only=True)
    siblings = SiblingsSerializer(many=True, required=False)
    parent = ParentSerializer(many=True, required=False)
    confirm_password = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = Person
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
            "confirm_password",
            "address",
            "birth_date",
            "siblings",
            "parent",
        )

    def save(self, request):

        user = Person.objects.create(
            username=request.POST.get("username"),
            password=request.POST.get("password"),
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            email=request.POST.get("email"),
            address=request.POST.get("address"),
            birth_date=request.POST.get("birth_date"),
            phone=request.POST.get("phone"),
        )

        return user

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        if data["email"] in list(Person.objects.all().values_list("email", flat=True)):
            raise serializers.ValidationError("Email already exists")
        if data["username"] in list(
            Person.objects.all().values_list("username", flat=True)
        ):
            raise serializers.ValidationError("Username already exists")
        return data


class RecursiveSerializer(serializers.ModelSerializer):

    """
        Recursive serializer to get parent details of a person.(Hierarchical serializer)
    """

    parent = serializers.SerializerMethodField(read_only=True)

    def get_parent(self, obj):
        return RecursiveSerializer(obj.parent.all(), many=True).data

    class Meta:
        model = Person
        fields = ("username", "id", "parent")


class RecursiveChildrenSerializer(serializers.ModelSerializer):

    """
        Recursive serializer to get children details of a person.(Hierarchical serializer)
    """

    children = serializers.SerializerMethodField(read_only=True)

    def get_children(self, obj):
        return RecursiveChildrenSerializer(
            Person.objects.filter(parent__id=obj.id), many=True
        ).data

    class Meta:
        model = Person
        fields = ("username", "id", "children")


class GrandParentsSerializer(serializers.ModelSerializer):

    """
        Serializer to get grandparent details of a person.
    """

    grandparents = serializers.SerializerMethodField(read_only=True)

    def get_grandparents(self, obj):
        result = {"username": obj.username, "id": obj.id, "grandparents": []}
        for parent in obj.parent.all():
            for grandparent in parent.parent.all():
                result["grandparents"].append(
                    {"username": grandparent.username, "id": grandparent.id}
                )
        return result

    class Meta:
        model = Person
        fields = ("username", "id", "grandparents")


class EditUserSerializer(serializers.ModelSerializer):

    """
        Serializer to edit/Update a person.
    """

    class Meta:
        model = Person
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "address",
            "email",
            "phone",
            "birth_date",
            "siblings",
            "parent",
        )

    def validate(self, data):
        if data["username"] != self.instance.username:
            raise serializers.ValidationError("Username once set cannot be changed.")
        if data["email"] != self.instance.email:
            raise serializers.ValidationError("Email once set cannot be changed.")

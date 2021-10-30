from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet


from .models import Person
from .serializers import (
    PersonDataSerializer,
    PersonRegistrationSerializer,
    SiblingsSerializer,
    EditUserSerializer,
    ParentSerializer,
    RecursiveChildrenSerializer,
    GrandParentsSerializer,
    CousinsSerializer,
)


class PersonViewSet(ReadOnlyModelViewSet):

    """
        Viewset for getting details of all persons, single person,
        siblings, parents, children, grandchildren, cousins.
        Also for editing and deleting person.

    """

    serializer_class = PersonRegistrationSerializer
    queryset = Person.objects.all()

    @action(detail=False)
    def get_list(self, request):
        try:
            serializer = PersonDataSerializer(self.queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)})

    @action(detail=True)
    def get_person(self, request, pk=None):
        try:
            serializer = self.get_serializer(Person.objects.get(id=pk))
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)})

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated, IsAdminUser],
    )
    def delete_person(self, request, pk=None):
        try:
            Person.objects.get(id=pk).delete()
            return Response(
                status=200, data={"message": f"Person deleted with id {str(pk)}"}
            )
        except Exception as e:
            return Response(status=400, data={"message": str(e)})

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated])
    def edit_person(self, request, pk=None):
        try:
            person = Person.objects.get(id=pk)
            print(request)
            # import pdb
            # pdb.set_trace()
            data = EditUserSerializer(person, data=request.data, partial=True)
            if data.is_valid(raise_exception=True):
                data.save()
            else:
                data = "Invalid data"
        except Exception as e:
            data = str(e)

        return Response(data)

    @action(detail=True)
    def get_siblings(self, request, pk=None):
        try:
            siblings = Person.objects.get(id=pk).siblings
            data = (
                SiblingsSerializer(siblings, many=True).data
                if siblings.count()
                else "No siblings"
            )
        except Exception as e:
            data = str(e)
        return Response(data)

    @action(detail=True)
    def get_parents(self, request, pk=None):
        try:
            parents = Person.objects.get(id=pk).parent
            data = (
                ParentSerializer(parents, many=True).data
                if parents.count()
                else "No parents"
            )
        except Exception as e:
            data = str(e)
        return Response(data)

    @action(detail=True)
    def get_children(self, request, pk=None):
        try:
            person = Person.objects.get(id=pk)
            data = (
                RecursiveChildrenSerializer(person).data
                if Person.objects.filter(parent__id=person.id).count()
                else "No children"
            )
        except Exception as e:
            data = str(e)
        return Response(data)

    @action(detail=True)
    def get_grandparents(self, request, pk=None):
        try:
            person = Person.objects.get(id=pk)
            data = (
                GrandParentsSerializer(person).data
                if person.parent.count()
                else "No grand parents"
            )
            if type(data) != str:
                data = {
                    "username": person.username,
                    "id": person.id,
                    "grandparents": [gp for gp in data["grandparents"]["grandparents"]][
                        :2
                    ],
                }
        except Exception as e:
            data = str(e)

        return Response(data)

    @action(detail=True)
    def get_cousins(self, request, pk=None):
        try:
            person = Person.objects.get(id=pk)
            person_parents = [i for i in person.parent.all()]
            cousin_parents = [i.siblings.all() for i in person_parents]
            cousin_parent_ids = []
            for i in cousin_parents:
                for j in i:
                    if j:
                        cousin_parent_ids.append(j.id)
            data = (
                CousinsSerializer(
                    Person.objects.filter(parent__in=cousin_parent_ids), many=True
                ).data
                if cousin_parent_ids
                else "No Cousins"
            )
        except Exception as e:
            data = str(e)
        return Response(data)


class RegisterApiView(CreateAPIView):

    """
        API for creating new person/user.
    """

    model = get_user_model()
    permission_classes = [permissions.AllowAny]  # Or anon users can't register
    serializer_class = PersonRegistrationSerializer

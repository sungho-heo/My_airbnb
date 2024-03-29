from django.http import Http404
from django.views.generic import ListView, DetailView, View, UpdateView, FormView
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin 
from users import mixins as user_mixins
from . import models, forms


class HomeView(ListView):

    """ Home view Definition """

    model = models.Room
    paginate_by = 12
    paginate_orphans = 5
    ordering = "created"
    context_object_name = "rooms"

@method_decorator(login_required, name="dispatch")
class RoomDetail(DetailView):

    """ Room Detail Definition """
    model = models.Room
        


class SearchView(View):

    """ Searchview Definition """
    #django searchform 구현
    def get(self, request):

        country = request.GET.get('country')

        if country:
            
            form = forms.SearchForm(request.GET)

            if form.is_valid():
            
                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                bedrooms = form.cleaned_data.get("bedrooms")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")

                filter_args = {}

                if city != "Anywhere":
                    filter_args["city__startswith"] = city
                
                filter_args["country"] = country
                
                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price__lte"] = price

                if guests is not None:
                    filter_args["guests__gte"] = guests

                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms

                if beds is not None:
                    filter_args["beds__gte"] = beds

                if baths is not None:
                    filter_args["baths__gte"] = baths
                
                if instant_book is True:
                    filter_args["instant_book"] = True
                
                if superhost is True:
                    filter_args["host__superhost"] = True

                for amenity in amenities:
                    filter_args["amenities"] = amenity
                        
                for facility in facilities:
                    filter_args["facilities"] = facility

                qs = models.Room.objects.filter(**filter_args).order_by("created")

                paginator = Paginator(qs, 10, orphans=5)

                page = request.GET.get("page", 1)

                rooms = paginator.get_page(page)


                return render(request, "rooms/search.html", {"form": form, "rooms": rooms})

        else:

            form = forms.SearchForm()
        return render(request, "rooms/search.html", {"form": form})
    
class EditRoomView(user_mixins.LoggedInOnlyView,UpdateView):

    """ Edit Room Definition """

    model = models.Room
    template_name = "rooms/room_edit.html"
    fields= (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )
    
    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

class RoomPhotoView(user_mixins.LoggedInOnlyView, DetailView):

    """ Room photo Definition """

    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "Can't delete that photo ")
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo Deleted!")
        return redirect(reverse("rooms:photos", kwargs = {"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))            


class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    
    model = models.Photo
    template_name ="rooms/photo_edit.html"
    pk_url_kwarg = "photo_pk"
    success_message = "Photo Updated!"
    fields = ("caption",)

    def get_success_message(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk": room_pk})


class AddPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, FormView):
    template_name = "rooms/photo_create.html"
    form_class = forms.CreatePhotoForm

    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        form.save(pk)
        messages.success(self.request, "Photo Uploaded")
        return redirect(reverse("rooms:photos", kwargs = {"pk": pk}))

class CreateRoomView(user_mixins.LoggedInOnlyView, FormView):

    form_class = forms.CreateRoomForm
    template_name = "rooms/room_create.html"

    def form_valid(self, form):
        room = form.save()
        room.host =  self.request.user
        room.save()
        form.save_m2m()
        messages.success(self.reqeust, "Photo Uploaded")
        return redirect(reverse("rooms:details", kwargs = {"pk": room.pk}))

        





    #python 으로 search 구현
    # city = request.GET.get('city', "Anywhere")
    # city = str.capitalize(city)
    # country = request.GET.get('country', "KR")
    # room_type= int(request.GET.get('room_type', 0))
    # price= int(request.GET.get('price' ,0))
    # guests= int(request.GET.get("guests" ,0))
    # bedrooms= int(request.GET.get("bedrooms" ,0))
    # beds= int(request.GET.get("beds", 0))
    # baths= int(request.GET.get("baths", 0))
    # instant = bool(request.GET.get("instant",False))
    # superhost = bool(request.GET.get("superhost", False))
    # s_amenities = request.GET.getlist("amenities")
    # s_facilities = request.GET.getlist("facilities")
    # form = {
    #     "city": city,
    #     "s_room_type": room_type,
    #     "s_country": country,
    #     "price": price,
    #     "guests": guests,
    #     "bedrooms": bedrooms,
    #     "beds": beds,
    #     "baths": baths,
    #     "s_amenities": s_amenities,
    #     "s_facilities": s_facilities,
    #     "instant": instant,
    #     "superhost": superhost,
    # }

    # room_types = models.RoomType.objects.all()
    # amenities = models.Amenity.objects.all()
    # facilities = models.Facility.objects.all()
    
    # choices = {
    #     "countries": countries,
    #     "room_types": room_types,
    #     "amenities": amenities,
    #     "facilities": facilities,
    # }
    
    # filter_args = {}

    # if city != "Anywhere":
    #     filter_args["city__startswith"] = city
    
    # if room_type != 0:
    #     filter_args["room_type__pk"] = room_type

    # if price != 0:
    #     filter_args["price__lte"] = price

    # if guests != 0:
    #     filter_args["guests__gte"] = guests

    # if bedrooms != 0:
    #     filter_args["bedrooms__gte"] = bedrooms

    # if beds != 0:
    #     filter_args["beds__gte"] = beds

    # if baths != 0:
    #     filter_args["baths__gte"] = baths
    
    # if instant is True:
    #     filter_args["instant_book"] = True
    
    # if superhost is True:
    #     filter_args["host__superhost"] = True

    # if len(s_amenities) > 0:
    #     for s_amenity in s_amenities:
    #         filter_args["amenities__pk"] = int(s_amenity)
            
    # if len(s_facilities) > 0:
    #     for s_facility in s_facilities:
    #         filter_args["facilities__pk"] = int(s_facility)

    
    
    
    
    # rooms = models.Room.objects.filter(**filter_args)
    # return render(request, "rooms/search.html",{**form, **choices, "rooms": rooms})


# 함수형 detailview
# def room_detail(request, pk):
    
#     try:
#         room = models.Room.objects.get(pk=pk)
#         return render(request, "rooms/detail.html", context={"room":room})
#     except models.Room.DoesNotExist:
#         raise Http404  





    # django +python 구현 방식
# def all_rooms(request):
#     page = request.GET.get("page",1)
#     room_list = models.Room.objects.all()
#     paginator = Paginator(room_list, 10, orphans=5)
#     try:
#         rooms = paginator.page(int(page))
#         return render(request, "rooms/home.html", context={"page": rooms,},)
#     except EmptyPage:
#         return redirect("/")

    # Python만 사용해서  page 구현방식
    # page = request.GET.get("page", 1)
    # page = int(page or 1)
    # page_size = 10
    # limit = page_size * page
    # offset = limit - page_size
    # all_rooms = models.Room.objects.all()[offset:limit]
    # page_count = ceil(models.Room.objects.count() / page_size)


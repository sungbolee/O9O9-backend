import json

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Q

from .models        import MainCategory, SubCategory, Product, WatchList
from user.models    import User
from order.models   import Order, OrderStatus, OrderItem
from review.models  import Review
from user.utils     import login_decorator


class CategoriesView(View):
    def get(self, request):
        try:
            main_categories = MainCategory.objects.all()

            result = [
                {
                    'id'   : category.id,
                    'name' : category.name
                } for category in main_categories
            ]
            return JsonResponse({'data': result}, status=200)
        except ValueError:
            return JsonResponse({'message': "INVALID_KEY"}, status=400)


class ProductsView(View):
    def get(self, request):
        try:
            main_category_id = request.GET.get('main')
            sub_category_id  = request.GET.get('sub')
            query = Q()

            if main_category_id:
                if MainCategory.objects.filter(id=main_category_id).exists():
                    query &= Q(maincategory_id=main_category_id)
                else:
                    return JsonResponse({'message': "NON_EXISTING_CATEGORY"}, status=401)
            elif sub_category_id:
                if SubCategory.objects.filter(id=sub_category_id).exists():
                    query &= Q(subcategory_id=sub_category_id)
                else:
                    return JsonResponse({'message': "NON_EXISTING_CATEGORY"}, status=401)

            products = Product.objects.filter(query)

            result = [
                {
                    "id": product.id,
                    "image_url": product.thumbnail_image,
                    "title": product.name,
                    "price": product.price,
                    "brand": product.brand.name,
                    "watch_list": product.watch_list.count(),
                    "buy_count": product.buy_count
                } for product in products
            ]
            return JsonResponse({'data': result}, status=200)
        except ValueError:
            return JsonResponse({'message': "INVALID_KEY"}, status=400)


class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects. \
                select_related('maincategory',
                               'subcategory',
                               'brand',
                               'more_information',
                               'seller_information',
                               'exchange'
                               ).get(id=product_id)

            result = {
                "maincategory_id"     : product.maincategory.id,
                "subcategory_id"      : product.subcategory.id,
                "image_url"           : product.thumbnail_image,
                "detailproduct_image" : product.detail_image,
                "title"               : product.name,
                "price"               : product.price,
                "brand"               : product.brand.name,
                "watch_list"          : product.watch_list.count(),
                "buy_count"           : product.buy_count,
                "more_information"    : {
                    "tax_status"              : product.more_information.tax_status,
                    "receipt"                 : product.more_information.receipt,
                    "business_classification" : product.more_information.business_classification,
                    "producer_importer"       : product.more_information.producer_importer,
                    "origin"                  : product.more_information.origin,
                    "manufacturing_date"      : product.more_information.manufacturing_date,
                    "shelf_life"              : product.more_information.shelf_life,
                    "storage_method"          : product.more_information.storage_method,
                    "delivery_period"         : product.more_information.delivery_period
                },
                "seller_information"  : {
                    "representative"  : product.seller_information.representative,
                    "business_number" : product.seller_information.business_number,
                    "phone_number"    : product.seller_information.phone_number,
                    "email"           : product.seller_information.email
                },
                "exchange"            : {
                    "return_shipping_fee" : product.exchange.return_shipping_fee,
                    "where_to_send"       : product.exchange.where_to_send,
                    "detail_information"  : product.exchange.detail_information,
                },
                "review": [
                    {
                        "satisfaction": review.satisfaction,
                        "content"     : review.content,
                        "created_at"  : review.created_at,
                        "username"    : review.user.username_id
                    } for review in product.review_set.all()
                ]
            }
            return JsonResponse({'data': result}, status=200)
        except ValueError:
            return JsonResponse({'message': 'VALUE_ERROR'}, status=400)
        except Product.DoesNotExist:
            return JsonResponse({'message': 'NO_PRODUCT_FOUND'}, status=404)


class WatchListView(View):
    @login_decorator
    def post(self, request):
        try:
            data          = json.loads(request.body)
            product       = Product.objects.get(id=data['product_id'])
            user          = request.user

            if WatchList.objects.filter(product_id=product.id, user_id=user.id).exists():
                WatchList.objects.filter(product_id=product.id, user_id=user.id).delete()
                return JsonResponse({'user_like': 'delete'}, status=200)

            watchlist = WatchList.objects.create(
                product_id=product.id,
                user_id=user.id
            )
            return JsonResponse({'user_like': 'true'}, status=200)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)

            # product_model.watch_list.add(user_model)
            # return JsonResponse({'message': 'SUCCESS'}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({'message': 'NON_EXISTING_PRODUCT'}, status=401)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)

    @login_decorator
    def delete(self, request):
        data = json.loads(request.body)
        user_id = request.user

        user_model = User.objects.get(id=user_id)
        product_model = Product.objects.get(id=data['product_id'])
        # if not product_model.essential:
        #     product_model.watch_list.add(user_model)
        # else:
        #     ProductGroup.objects.get(id=product_model.productgroup.id).product_set.all()[0].watch_list.remove(user_model)

        return JsonResponse({'message': 'SUCCESS'}, status=200)

import json

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Prefetch, Q, F

from .models        import MainCategory, SubCategory, Product, ProductGroup
from user.models    import User
from order.models   import Order, OrderStatus, OrderItem
from review.models  import Review
from user.utils     import check_user

class CategoriesView(View):
    def get(self, request):

        result = list(MainCategory.objects.all().order_by('name').values_list('name', flat=True))
        return JsonResponse({"data": result}, status=200)

class ProductsView(View):
    def get(self, request):
        try:
            main_category_id = request.GET.get('main', None)
            sub_category_id = request.GET.get('sub', None)
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

            result = [{
                "id": product.id,
                "image_url": product.thumbnail_image,
                "title": product.name,
                "price": product.price,
                "brand": product.brand.name,
                "watch_list": product.watch_list.count(),
                "buy_count": product.buy_count
            } for product in products]

            group_products = ProductGroup.objects.prefetch_related('product_set')
            nongroup_products = Product.objects.select_related('brand').filter(query, essential=False)

            product_list = []
            nonproduct_list = []

            for group_product in group_products:
                if not group_product.product_set.all()[0]:
                    continue
                if group_product.product_set.all()[0].maincategory_id != query:
                    continue

                product_list.append({
                    "id"             : group_product.product_set.all()[0].id,
                    "image_url"      : group_product.product_set.all()[0].thumbnail_image,
                    "title"          : group_product.name,
                    "price"          : group_product.product_set.all()[0].price,
                    "brand"          : group_product.product_set.all()[0].brand.name,
                    "watch_list"     : group_product.product_set.all()[0].watch_list.count(),
                    "buy_count"      : group_product.product_set.all()[0].buy_count
                })

            for nongroup_product in nongroup_products:
                nonproduct_list.append({
                    "id"        : nongroup_product.id,
                    "image_url" : nongroup_product.thumbnail_image,
                    "title"     : nongroup_product.name,
                    "price"     : nongroup_product.price,
                    "brand"     : nongroup_product.brand.name,
                    "watch_list": nongroup_product.watch_list.count(),
                    "buy_count" : nongroup_product.buy_count
                })

            result = product_list + nonproduct_list
            return JsonResponse({'productList': result}, status=200)

        except ValueError:
            return JsonResponse({"message": "INVALID_KEY"}, status=400)

class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.select_related('maincategory',
                                                     'subcategory',
                                                     'brand',
                                                     'productgroup',
                                                     'more_information',
                                                     'seller_information',
                                                     'exchange'
                                                     ).get(id=product_id)

            product_detail = {
                "maincategory_id"     : product.maincategory.id,
                "subcategory_id"      : product.subcategory.id,
                "image_url"           : product.thumbnail_image,
                "detailproduct_image" : product.detail_image,
                "title"               : product.name if not product.essential else product.productgroup.name,
                "price"               : product.price,
                "brand"               : product.brand.name,
                "watch_list"          : product.watch_list.count() if not product.essential else ProductGroup.objects.get(id=product.productgroup.id).product_set.all()[0].watch_list.count(),
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
                # "review": [review.content for review in product.review_set.all()]
            }

        except ValueError:
            return JsonResponse({'message': 'VALUE_ERROR'}, status=400)

        except Product.DoesNotExist:
            return JsonResponse({'message': 'NO_PRODUCT_FOUND'}, status=404)

        return JsonResponse({'product': product_detail}, status=200)

class ReviewView(View):
    def get(self, request, product_id):
        # try:
        product_model = Product.objects.get(id=product_id).id

        #     reviews = [{"satisfaction": review.satisfaction,
        #                 "content": review.content,
        #                 "created_at": review.created_at,
        #                 "username": review.user.username_id
        #                 } for review in product_model.review_set.all()]
        # except KeyError:
        #     return JsonResponse({'message': 'KEY_ERROR'}, status=401)

        return JsonResponse({'reviews': product_model}, status=200)

class WatchListView(View):
    @check_user
    def post(self, request):
        data = json.loads(request.body)
        user_id = request.user
        user_model = User.objects.get(id=user_id)
        product_model = Product.objects.get(id=data['product_id'])

        if not product_model.essential:
            product_model.watch_list.add(user_model)
        else:
            ProductGroup.objects.get(id=product_model.productgroup.id).product_set.all()[0].watch_list.add(user_model)

        return JsonResponse({'message': 'SUCCESS'}, status=200)

    @check_user
    def delete(self, request):
        data = json.loads(request.body)
        user_id = request.user

        user_model = User.objects.get(id=user_id)
        product_model = Product.objects.get(id=data['product_id'])
        if not product_model.essential:
            product_model.watch_list.add(user_model)
        else:
            ProductGroup.objects.get(id=product_model.productgroup.id).product_set.all()[0].watch_list.remove(user_model)

        return JsonResponse({'message': 'SUCCESS'}, status=200)

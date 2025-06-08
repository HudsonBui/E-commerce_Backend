import pandas as pd
import json

from django.db import transaction
from django.core.management.base import BaseCommand
from core.models import (
    Category,
    Product,
    ProductImage,
    ProductVariant,
    ProductDetailInformation,
    ProductDetail)


def get_or_create_category_hierarchy(breadcrumbs_list):
    parent = None
    for breadcrumb in breadcrumbs_list:
        name = breadcrumb['name']
        category, _ = Category.objects.get_or_create(
            name=name,
            parent_category=parent,
        )
        parent = category

    return category  # Return the leaf category created or found


def normalize_weight_unit(weight_unit):
    unit_map = {
        'pound': 'lb',
        'ounce': 'oz',
        'gram': 'g',
        'kilogram': 'kg',
    }

    return unit_map.get(
        weight_unit.lower(),
        weight_unit.lower()
    ) if weight_unit else 'g'


class Command(BaseCommand):
    """Imports product data from a CSV file into the database"""

    def add_arguments(self, parser):
        """
        Adds command line arguments for the import command.
        """
        parser.add_argument(
            'csv_file_path',
            type=str,
            help='Path to the CSV file to import'
        )

    def handle(self, *args, **options):
        """Handle ingest data from csv file."""
        csv_file_path = options['csv_file_path']
        self.stdout.write(
            self.style.SUCCESS(f'Starting import from {csv_file_path}')
        )

        df = pd.read_csv(csv_file_path)

        for index, row in df.iterrows():
            with transaction.atomic():  # Ensure atomicity for each product
                try:
                    breadcrumbs = json.loads(row['breadcrumbs'])
                    variants = json.loads(
                        row['variants']) if pd.notna(row['variants']) else []
                    product_details = json.loads(row['Product detail'])
                    image_urls = json.loads(row['imageUrls'])
                    features = json.loads(
                        row['features']) if pd.notna(row['features']) else []

                    # Create category hierarchy and get leaf category
                    leaf_category = get_or_create_category_hierarchy(
                        breadcrumbs
                    )

                    # Create Product instance
                    description = "About this item:\n" + \
                        "\n • ".join(features)
                    product = Product(
                        name=row['name'],
                        description=description,
                        material=row['material']
                        if pd.notna(row['material']) else None,
                        weight=float(row['weight_value'])
                        if pd.notna(row['weight_value']) else None,
                        weight_unit=normalize_weight_unit(
                            (row['weight_unit']
                                if pd.notna(row['weight_unit']) else None)
                        ),
                        stock_quantity=int(row['quantity'])
                        if pd.notna(row['quantity']) else 0,
                        node_name=row['nodeName']
                        if pd.notna(row['nodeName']) else None,
                        style=row['style'] if pd.notna(row['style']) else None,
                        currency=row['currency'],
                        price=float(row['listedPrice'])
                        if pd.notna(row['listedPrice']) else 0.00,
                        average_rating=float(row['rating'])
                        if pd.notna(row['rating']) else 0.00,
                        review_count=int(row['reviewCount'])
                        if pd.notna(row['reviewCount']) else 0,
                        review_count_sample=0,
                        average_rating_sample=0.00
                    )
                    product.save()
                    product.category.add(leaf_category)

                    # Create ProductImage instances
                    for i, url in enumerate(image_urls):
                        ProductImage.objects.create(
                            product=product,
                            url=url,
                            is_primary=(i == 0)  # First image is primary
                        )

                    # Parse variants and create ProductVariant
                    # and ProductDetail instances
                    colors = {v['color'] for v in variants if 'color' in v}
                    sizes = {v['size'] for v in variants if 'size' in v}

                    if variants:
                        if colors and sizes:
                            # Create combinations of colors and sizes
                            for color in colors:
                                for size in sizes:
                                    variant = ProductVariant.objects.create(
                                        product=product,
                                        color=color,
                                        size=size,
                                        stock_quantity=row['quantity']
                                    )
                                    ProductDetail.objects.create(
                                        product=product,
                                        detail_variant=variant,
                                        price=float(row['listedPrice'])
                                        if pd.notna(row['listedPrice'])
                                        else 0.00,
                                        sale_price=float(row['salePrice'])
                                        if pd.notna(row['salePrice']) else 0.00
                                    )
                        elif colors:
                            # Only colors, size is None
                            for color in colors:
                                variant = ProductVariant.objects.create(
                                    product=product,
                                    color=color,
                                    size=None,
                                    stock_quantity=0
                                )
                                ProductDetail.objects.create(
                                    product=product,
                                    detail_variant=variant,
                                    price=float(row['listedPrice'])
                                    if pd.notna(row['listedPrice']) else 0.00,
                                    sale_price=float(row['salePrice'])
                                    if pd.notna(row['salePrice']) else 0.00
                                )
                        elif sizes:
                            # Only sizes, use color column
                            # or default to "Standard"
                            color = row['color'] \
                                if pd.notna(row['color']) else "Standard"
                            for size in sizes:
                                variant = ProductVariant.objects.create(
                                    product=product,
                                    color=color,
                                    size=size,
                                    stock_quantity=0
                                )
                                ProductDetail.objects.create(
                                    product=product,
                                    detail_variant=variant,
                                    price=float(row['listedPrice'])
                                    if pd.notna(row['listedPrice']) else 0.00,
                                    sale_price=float(row['salePrice'])
                                    if pd.notna(row['salePrice']) else 0.00
                                )
                    else:
                        # No variants, create a single ProductDetail
                        # with detail_variant=None
                        ProductDetail.objects.create(
                            product=product,
                            detail_variant=None,
                            price=float(row['listedPrice'])
                            if pd.notna(row['listedPrice']) else 0.00,
                            sale_price=float(row['salePrice'])
                            if pd.notna(row['salePrice']) else 0.00
                        )

                    # Create ProductDetailInformation instances
                    for detail in product_details:
                        ProductDetailInformation.objects.create(
                            product=product,
                            detail_name=detail['name'],
                            detail_value=detail['value']
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing row {index}: {e}')
                    )
                    self.stdout.write(self.style.WARNING(f'Row data: {row}'))
                    # Decide if you want to continue or stop on error

        self.stdout.write(self.style.SUCCESS('Finished import process.'))

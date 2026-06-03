import uuid

from django.test import TestCase

from apps.categories.models import Category
from apps.categories.selectors import build_category_tree, get_category_tree


class CategoryTreeTests(TestCase):
    def setUp(self) -> None:
        suffix = uuid.uuid4().hex[:8]

        self.parent = Category.objects.create(is_active=True, sort_order=1)
        self.parent.set_current_language("sr")
        self.parent.name = "Parent"
        self.parent.slug = f"parent-{suffix}"
        self.parent.save()

        self.child = Category.objects.create(
            is_active=True,
            parent=self.parent,
            sort_order=1,
        )
        self.child.set_current_language("sr")
        self.child.name = "Child"
        self.child.slug = f"child-{suffix}"
        self.child.save()

        self.grandchild = Category.objects.create(
            is_active=True,
            parent=self.child,
            sort_order=1,
        )
        self.grandchild.set_current_language("sr")
        self.grandchild.name = "Grandchild"
        self.grandchild.slug = f"grandchild-{suffix}"
        self.grandchild.save()

    def test_category_tree_lists_roots_only_at_top_level(self) -> None:
        tree = get_category_tree("sr")
        root_ids = [node.category.pk for node in tree]
        self.assertEqual(root_ids, [self.parent.pk])
        self.assertEqual(len(tree[0].children), 1)
        self.assertEqual(tree[0].children[0].category.pk, self.child.pk)
        self.assertEqual(len(tree[0].children[0].children), 1)
        self.assertEqual(
            tree[0].children[0].children[0].category.pk,
            self.grandchild.pk,
        )

    def test_build_subtree_starts_at_direct_children(self) -> None:
        from apps.categories.selectors import get_category_subtree

        subtree = get_category_subtree(self.parent, "sr")
        self.assertEqual(len(subtree), 1)
        self.assertEqual(subtree[0].category.pk, self.child.pk)
        self.assertEqual(len(subtree[0].children), 1)
        self.assertEqual(subtree[0].children[0].category.pk, self.grandchild.pk)

    def test_orphan_category_becomes_root(self) -> None:
        inactive_parent = Category.objects.create(is_active=False)
        inactive_parent.set_current_language("sr")
        inactive_parent.name = "Inactive"
        inactive_parent.slug = f"inactive-{uuid.uuid4().hex[:8]}"
        inactive_parent.save()

        orphan = Category.objects.create(is_active=True, parent=inactive_parent)
        orphan.set_current_language("sr")
        orphan.name = "Orphan"
        orphan.slug = f"orphan-{uuid.uuid4().hex[:8]}"
        orphan.save()

        tree = build_category_tree(
            Category.objects.filter(is_active=True).prefetch_related("translations"),
            root_parent_id=None,
        )
        root_ids = {node.category.pk for node in tree}
        self.assertIn(self.parent.pk, root_ids)
        self.assertIn(orphan.pk, root_ids)

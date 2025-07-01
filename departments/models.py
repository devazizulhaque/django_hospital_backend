from django.db import models

class Department(models.Model):
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',  # ডিপার্টমেন্টের চাইল্ড ডিপার্টমেন্টগুলো পেতে
        verbose_name="Parent Department",
        help_text="Select a parent department (optional)."
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Department Name",
        help_text="Enter a unique department name."
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Short description about the department."
    )
    icon = models.ImageField(
        upload_to='department_icons/',
        blank=True,
        null=True,
        verbose_name="Department Icon",
        help_text="Upload department icon (optional)."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Uncheck to deactivate the department without deleting it."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        db_table = 'departments'
        indexes = [
            models.Index(fields=['parent']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
        permissions = [
            ("can_view_department", "Can view department"),
        ]

    def __str__(self):
        # Parent সহ নাম দেখানোর জন্য
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def soft_delete(self):
        self.is_active = False
        self.save()

    def get_children(self):
        # এই ডিপার্টমেন্টের সরাসরি চাইল্ড ডিপার্টমেন্টগুলো পেতে
        return self.children.filter(is_active=True)

    def get_all_children(self):
        # রিকার্সিভলি সব চাইল্ড ডিপার্টমেন্ট পেতে
        all_children = []
        for child in self.get_children():
            all_children.append(child)
            all_children.extend(child.get_all_children())
        return all_children
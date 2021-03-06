"""forms.py defines the input fields for data entry pages generated by Django.

The classes contained here describe sets of data entry fields that django uses
to construct form pages and validate the incoming information.

Note
____
    Fields referencing databse entries (e.g. new_pv's use of PV.objects.all())
    MUST be placed inside the init funciton. Failure to do
    so will break djang's ability to migrate and has the potential to interfere
    with other features. 

"""

from django import forms
from .models import Alert, Pv, Trigger#, PVname
from account_mgr_app.models import Profile
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


class configTrigger(forms.Form):
    """Define the fields for an individual trigger

    Attributes
    __________
        new_pv : forms.ChoiceField
            Provides dropdown selection of PV's to link to this trigger. This 
            attr is defined in the __init__ due to its reliance on DB items.

        new_compare : forms.ChoiceField
            Describes the comparison operation between the PV's value and 
            the triggering value (new_value)

        new_name : forms.CharField
            Changes to the trigger name can be entered in this field

        new_value : forms.FloatField
            Changes to the triggering value can be entered in this field

    """
    def __init__(self,*args,**kwargs):
        """Constrct the object
        """
        super().__init__(*args,**kwargs)
        self.fields['new_pv'] = forms.ChoiceField(
            label = 'PV name',
            # use this to sort alphabetiaclly if necessary
            # sorted([(np.random.random(),np.random.random()) for x in range(10)],key=lambda s: s[1])
            choices = [(-1,None)] + [ (x.pk,x.name) for x in Pv.objects.all()],
            # choices = ["a,"b"],
            widget = forms.Select(
                attrs = {
                    'class':'custom-select',
                }
            )
        )
    

        self.fields['new_compare'] = forms.ChoiceField(
        label = 'Comparison',
        choices = [(-1,None)] + Trigger.compare_choices,
        widget = forms.Select(
            attrs = {
                'class':'custom-select',
                }
            )
        )
    
    
    new_name = forms.CharField(
        label = 'Trigger name',
        max_length = Trigger.name_max_length,
        widget = forms.TextInput( 
            attrs = {
                'class':'form-control',
                'type':'text',
            }
        )
    )
    # '''
    # new_pv = forms.ChoiceField(
    #     label = 'PV name',
    #     # use this to sort alphabetiaclly if necessary
    #     # sorted([(np.random.random(),np.random.random()) for x in range(10)],key=lambda s: s[1])
    #     choices = [(-1,None)] + [ (x.pk,x.name) for x in Pv.objects.all()],
    #     # choices = ["a,"b"],
    #     widget = forms.Select(
    #         attrs = {
    #             'class':'custom-select',
    #         }
    #     )
    # )
    # '''
    new_value = forms.FloatField(
        label = 'Value',
        required = False,
        widget = forms.NumberInput(
            attrs = {
                'class':'form-control',
            }
        )
    )

    # new_compare = forms.ChoiceField(
    #     label = 'Comparison',
    #     choices = [(-1,None)] + Trigger.compare_choices,
    #     widget = forms.Select(
    #         attrs = {
    #             'class':'custom-select',
    #         }
    #     )
    # )


    def clean_new_name(self):
        data = self.cleaned_data['new_name']
        # print("DATA:",data)
        # if len(data) <= 0 or data == None:
        #     raise forms.ValidationError(
        #         'Links must have unique anchors and URLs.',
        #         code='duplicate_links'
        #     )
        return data

    def clean_new_pv(self):
        data = self.cleaned_data['new_pv']
        if data == str(-1):
            data = None
        else:
            data = Pv.objects.get(pk=int(data))

        return data

    def clean_new_compare(self):
        data = self.cleaned_data['new_compare']
        if data == str(-1):
            data = None
        if data == "":
            data = None

        return data


class configAlert(forms.Form):#ModelForm
    """Define the fields for an alert. These are the editable fields that
    presented to users who have ownership over this alert.

    Attributes
    ----------
        new_owners : forms.MultipleChoiceField
            Provides dropdown selection of profiles who can own this object.
            The user can give ownership to themselves and others. This does NOT
            register these users to receive alerts. This attr is defined in 
            the __init__ due to its reliance on DB items.

        new_name : forms.CharField
            Changes to the alert name can be entered in this field.abs

        new_subscribe : forms.BooleanField
            Determines whether the current user is subscribed. Unike the owners
            field, registering others is not possible to prevent trolling.
            
    """

    class Meta:
        model = Alert

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.fields['new_owners'] = forms.MultipleChoiceField(
            label = 'Owners',
            # use this to sort alphabetiaclly if necessary
            # sorted([(np.random.random(),np.random.random()) for x in range(10)],key=lambda s: s[1])
            choices = [ (x.pk,x.user.username) for x in Profile.objects.all()],
            # choices = ["a,"b"],
            widget = forms.CheckboxSelectMultiple(
                attrs = {
                    'class':'form-control',
                }
            )
        )


    new_name = forms.CharField(
        label = 'Alert name',
        max_length = Alert.name_max_length,
        widget = forms.TextInput( 
            attrs = {
                'class':'form-control',
                'type':'text',
            }
        )
    )

    new_subscribe = forms.BooleanField(
        label = "Subscribed",
        required = False,
        # This is where the checkbox for alert readonly page shows up... Can't figure out how to change size
        widget = forms.CheckboxInput(
            attrs = {
                'class':'form-check-input',
                'type':'checkbox',
                #'size':'300'
            }
        )
    )

    new_lockout_duration = forms.DurationField(
        label = "Delay Between Successive Alerts",
        required = False,
        widget = forms.TimeInput(
            attrs = {
                'class':'form-control',
                'type':'text',
                'placeholder':'dd hh:mm:ss',
                #'data-toggle':'tooltip',
                #'data-placement':'top',
                #'title':'tooltip!',
            }
        )
    )
    

    def clean_new_subscribe(self):
        """Validate the subscription option

        Returns
        -------
            bool
                True if the user has selected the subscriber option

        Note
        ----
            Todo field isn't working? Confirm that this function works with 
            missing fields.
            This field can occasionally report None and is notorious for
            bugging after changes


        """
        
        if self.cleaned_data['new_subscribe']:
            data = True
        else:
            data = False

        return data


class subscribeAlert(forms.Form):
    """Define the fields for an alert. These fields are presented when the user
    does NOT own this alert. The only option is to subscribe.
    """
    class Meta:
        model = Alert

    new_subscribe = forms.BooleanField(
        label = "Subscribed",
        required = False,
        widget = forms.CheckboxInput(
            attrs = {
                'class':'form-check-input',
                'type':'checkbox',
            }
        )
    )
    def clean_new_subscribe(self):
        
        if self.cleaned_data['new_subscribe']:
            data = True
        else:
            data = False

        return data
    
    
class createPv(forms.ModelForm):
    class Meta:
        model = Pv
        fields = ['new_name']

    new_name = forms.CharField(
        label = 'PV name',
        max_length = Pv.name_max_length,
        widget = forms.TextInput( 
            attrs = {
                'class':'form-control',
                'type':'text',
            }
        )
    )
    # forms.ModelForm.Meta.fields.append(new_name)
     

class deleteAlert(forms.Form):
    class Meta:
        model = Alert
        fields = []
        
        
#class EditProfileForm(UserChangeForm):
#    
#    class Meta:
#        model = User 
#        fields = {
#            'username',
#            'email',
#            'password'
#        }

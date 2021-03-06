GLClient.controller('AdminFieldsCtrl', ['$scope', '$filter',
                    function($scope, $filter) {
    $scope.composable_fields = {};
    $scope.admin.field_templates.$promise
      .then(function(fields) {
        $scope.fields = fields;
        angular.forEach(fields, function(field, index) {
          $scope.composable_fields[field.id] = field;
          if (field.type == 'fieldgroup') {
            angular.forEach(field.children, function(field_c, index_c) {
              $scope.composable_fields[field_c.id] = field_c;
            });
          }
        });

      });

    $scope.deleteFromList = function(list, elem) {
      var idx = _.indexOf(list, elem);
      if (idx != -1) {
        list.splice(idx, 1);
      }
    };

    $scope.toggle_field = function(field, field_group) {
      $scope.field_group_toggled = true;
      if (field_group.children && (_.indexOf(field_group.children, field) !== -1)) {
        // Remove it from the fieldgroup 
        field.fieldgroup_id = "";
        $scope.admin.field_templates.push(field);
        $scope.deleteFromList(field_group.children, field);
      } else {
        // Add it to the fieldgroup 
        field.fieldgroup_id = field_group.id;
        field_group.children = field_group.children || [];
        field_group.children.push(field);
        $scope.admin.field_templates = $filter('filter')($scope.admin.field_templates, 
                                                         {id: '!'+field.id}, true);
      }
    }

    $scope.save_all = function () {
      angular.forEach($scope.admin.field_templates, function (field, key) {
        $scope.save_field(field, true);
      });
    };
    
    $scope.addField = function(new_field) {
      $scope.fields.push(new_field);
    };

    $scope.deleteField = function(field) {
      var idx = _.indexOf($scope.fields, field);
      $scope.fields.splice(idx, 1);
    };

    $scope.perform_delete = function(field) {
      $scope.admin.field_template['delete']({
        template_id: field.id
      }, function(){
        $scope.deleteField(field);
      });
    }

    $scope.create_field = function() {
      return $scope.admin.new_field_template('');
    };
  }
]);

GLClient.controller('AdminFieldsEditorCtrl', ['$scope',  '$modal',
  function($scope, $modal) {
    $scope.field_group_toggled = false;

    $scope.fieldDeleteDialog = function(field){
      var modalInstance = $modal.open({
          templateUrl:  'views/partials/field_delete.html',
          controller: 'ConfirmableDialogCtrl',
          resolve: {
            object: function () {
              return field;
            }
          }

      });

      modalInstance.result.then(
         function(result) { $scope.perform_delete(result); },
         function(result) { }
      );
    };


    $scope.isSelected = function (field) {
      // XXX this very inefficient as it cycles infinitely on the f in
      // admin.fields | filter:filterSelf ng-repeat even when you are not using
      // a field group.
      if (!$scope.field.children) {
        return false; 
      }
      return $scope.field.children.indexOf(field) !== -1;
    };

    function tokenize(input) {
      var result = input.replace(/[^-a-zA-Z0-9,&\s]+/ig, '');
      result = result.replace(/-/gi, "_");
      result = result.replace(/\s/gi, "-");
      return result;
    }

    $scope.typeSwitch = function (type) {
      if (_.indexOf(['checkbox', 'selectbox'], type) !== -1)
        return 'checkbox_or_selectbox';
      return type;
    };

    $scope.addOption = function (field) {
      field.options.push({});
    };

    $scope.delOption = function(field, option) {
      var index = field.options.indexOf(option);
      field.options.splice(index, 1);
   }

    $scope.save_field = function(field, called_from_save_all) {
      updated_field =  new $scope.admin.field(field);
      if ($scope.field_group_toggled) {
        $scope.field_group_toggled = false;
        if (!called_from_save_all) {
          $scope.save_all();
        }
      } else {
        $scope.update(updated_field);
      }
    };

    $scope.$watch('field.type', function (newVal, oldVal) {

      if (newVal && newVal !== oldVal) {
        $scope.field.options = [];
      }

    });

  }
]);

GLClient.controller('AdminFieldsAddCtrl', ['$scope',
  function($scope) {

    $scope.new_field = {};

    $scope.add_field = function() {
      var field = new $scope.create_field();

      field.label = $scope.new_field.label;
      field.description = $scope.new_field.label;
      field.type = $scope.new_field.type;

      if (field.type == 'tos') {
        field.options.push({'attrs':
          {
            'clause': '',
            'agreement_statement': ''
          }
        });
      }

      field.$save(function(new_field){
        $scope.addField(new_field);
        $scope.new_field = {};
      });

    }
  }
]);

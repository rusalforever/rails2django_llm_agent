class ApplicationController < ActionController::Base
  include ActiveStorage::SetCurrent
  # Only allow modern browsers supporting webp images, web push, badges, import maps, CSS nesting, and CSS :has.
  allow_browser versions: :modern

  protected
    def authorize_admin!
      redirect_to root_path, alert: "You don't have permission to view this page" if !current_admin
    end
end

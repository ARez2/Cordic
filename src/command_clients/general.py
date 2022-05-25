import nextcord
import nextcord.utils
from nextcord import PermissionOverwrite
from lib.utils import COLOR_GREEN


class GeneralClient():
    EVERYONE_OVERWRITE : PermissionOverwrite = None
    ROLE_OVERWRITE : PermissionOverwrite = None

    async def setup(self, args, user, guild, jiraclient):
        response_text = "Tip: Make sure all users aren't set to 'Invisible' as status"
        
        domain_and_project_name = args[0]
        rolename = f"project_{domain_and_project_name}_asignee"
        categoryname = f"Project {domain_and_project_name}"

        role = nextcord.utils.get(guild.roles, name=rolename)
        # Server hat noch keine Rolle mit dem namen
        if role is None:
            role = await guild.create_role(name=rolename)
            response_text += f" A new role called `{rolename}` has been created."
        
        
        category = nextcord.utils.get(guild.categories, name=categoryname)
        if category is None:
            category = await guild.create_category(categoryname)

            if self.EVERYONE_OVERWRITE is None:
                self.EVERYONE_OVERWRITE = PermissionOverwrite()
                self.EVERYONE_OVERWRITE.view_channel = False
                self.EVERYONE_OVERWRITE.connect = False
            # guild.default_role ist @everyone
            await category.set_permissions(guild.default_role, overwrite=self.EVERYONE_OVERWRITE)
            
            if self.ROLE_OVERWRITE is None:
                self.ROLE_OVERWRITE = PermissionOverwrite()
                self.ROLE_OVERWRITE.view_channel = True
                self.ROLE_OVERWRITE.read_message_history = True
                self.ROLE_OVERWRITE.read_messages = True
                self.ROLE_OVERWRITE.connect = True
            await category.set_permissions(role, overwrite=self.ROLE_OVERWRITE)

            await category.create_text_channel("General")
            #await category.create_voice_channel("Meeting Room")
            response_text += f" A new category called `{categoryname}` has been created and the role `{rolename}` has been configured for it."


        auto_assigned_someone = await self.auto_assign_users(domain_and_project_name, rolename, role, guild, jiraclient)
        if auto_assigned_someone:
            response_text += f" Users have been automatically assigned to the `{rolename}` role."
        
        return {
            "title": f"The project `{domain_and_project_name}` has been set up.",
            "description": response_text,
            "color": COLOR_GREEN,
        }
    

    async def auto_assign_users(self, domain_and_project_name, rolename, role, guild, jiraclient):
        auto_assigned_someone = False
        async for user in guild.fetch_members(limit=None):
            if user.bot: continue
            project_embed = jiraclient.get_projects_by_user(user)
            if project_embed.get("fields") is None:
                continue
            project_list = project_embed["fields"]["projects"]
            if len(project_list) <= 0:
                continue
            for project in project_list.split(" ,"):
                project = project.split(":")[0]
                if project.lower() == domain_and_project_name.lower() and nextcord.utils.get(user.roles, name=rolename) is None:
                    auto_assigned_someone = True
                    await user.add_roles(role)
        return auto_assigned_someone
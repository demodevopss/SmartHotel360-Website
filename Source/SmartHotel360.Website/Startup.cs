using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
using SmartHotel360.PublicWeb.Models.Settings;
using SmartHotel360.PublicWeb.Services;
using System;
using Microsoft.Extensions.Hosting;

namespace SmartHotel360.PublicWeb
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        public void ConfigureServices(IServiceCollection services)
        {
            services.AddControllersWithViews();
            services.AddOptions();
            services.Configure<LocalSettings>(Configuration);
            services.AddSingleton<SettingsService>( (sp) => SettingsService.Load(sp.GetService<IOptions<LocalSettings>>().Value));

            // Our custom services
            if (!string.IsNullOrEmpty(Configuration["USE_NULL_TESTIMONIALS_SERVICE"]))
            {
                services.AddSingleton<ICustomerTestimonialService>(new NullCustomerTestimonialService());
            } else
            {
                services.AddSingleton<ICustomerTestimonialService, PositiveTweetService>();
            }
        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }
            else
            {
                app.UseExceptionHandler("/Home/Error");
            }

            app.UseStaticFiles();

            app.UseRouting();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllerRoute(
                    name: "default",
                    pattern: "{controller=Home}/{action=Index}/{id?}");

                // React SPA fallback to index.html
                endpoints.MapFallbackToFile("index.html");
            });
        }
    }
}
